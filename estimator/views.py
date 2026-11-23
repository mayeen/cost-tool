import math
from datetime import timedelta

from django.shortcuts import render

from .calculations.cost import add_totals, benefit_amount, year_result
from .calculations.immigration import build_cost_rows, build_verdict, months_between, pick_visa
from .calculations.inputs import EstimatorInput
from .forms import EstimatorForm
from .rules import switzerland as ch
from .rules import uk
from .rules.immigration import SOURCES, get_route

#tab2
SECTIONS = [
    ("work_permit", "Work permit"),
    ("business_visit", "Business visit before the assignment"),
    ("passport", "Passport"),
    ("employer_duty", "Employer duty"),
]

def year_labels(inp):
    count = math.ceil(months_between(inp.start_date, inp.end_date) / 12)
    first = inp.start_date.year
    return [f"Year {n} ({first + n - 1}/{(first + n) % 100:02d})" for n in range(1, count + 1)]

#Tab 1
def build_cost_result(inp):
    labels = year_labels(inp)
    numbers = range(1, len(labels) + 1)
    years = [year_result(inp, n) for n in numbers]

    def uk_src(keys):
        return [uk.SOURCES[k] for k in keys]

    def ch_src(keys):
        return [ch.SOURCES[k] for k in keys]

    def each_year(key):
        return [y[key] for y in years]

    sections = [
        {
            "title": "1. Home pay",
            "subtotal_label": "Home pay",
            "rows": [
                {"name": "Base salary", "tag": "", "sources": [],
                 "amounts": [inp.home_currency_to_host_currency(inp.base_salary_home) for n in numbers]},
                {"name": "Bonus", "tag": "", "sources": [],
                 "amounts": [inp.home_currency_to_host_currency(inp.bonus_home) for n in numbers]},
            ],
        },
        {
            "title": "2. Assignment benefits",
            "subtotal_label": "Assignment benefits",
            "rows": [
                {"name": b["name"], "tag": b["tag"], "sources": uk_src(b["source"]),
                 "amounts": [benefit_amount(inp, b, n) for n in numbers]}
                for b in uk.BENEFITS
            ],
        },
        {
            "title": "3. Host tax and charges paid by the employer",
            "subtotal_label": "Host tax and charges",
            "rows": [
                {"name": "UK income tax, including tax on tax",
                 "tag": "Grossed up, see working below",
                 "sources": uk_src(uk.INCOME_TAX["source"] + uk.GROSS_UP["source"]),
                 "amounts": each_year("uk_tax")},
                {"name": "UK employer National Insurance",
                 "tag": "Swiss system applies, see below",
                 "sources": uk_src(uk.SOCIAL_SECURITY["source"]),
                 "amounts": [uk.SOCIAL_SECURITY["uk_employer_ni"] for n in numbers]},
            ],
        },
        {
            "title": "4. Deductions",
            "subtotal_label": "Deductions",
            "subtract": True,
            "rows": [
                {"name": "Hypothetical Swiss income tax",
                 "tag": "Federal, cantonal and communal",
                 "sources": ch_src(ch.HYPO_TAX["source"]),
                 "amounts": each_year("swiss_tax")},
                {"name": "Hypothetical Swiss social security",
                 "tag": "AHV/IV/EO and unemployment insurance",
                 "sources": ch_src(ch.SOCIAL_SECURITY["source"]),
                 "amounts": each_year("swiss_ss")},
            ],
        },
    ]

    working = [
        {
            "year": label,
            "start_income": y["income"],
            "rounds": y["rounds"][:4],
            "round_count": len(y["rounds"]),
            "final": y["rounds"][-1],
        }
        for label, y in zip(labels, years)
    ]

    return {
        "years": labels,
        "sections": sections,
        "totals": add_totals(sections),
        "social_security": {
            "title": uk.SOCIAL_SECURITY["title"],
            "text": uk.SOCIAL_SECURITY["text"],
            "sources": uk_src(uk.SOCIAL_SECURITY["source"]),
        },
        "working": working,
        "assumptions": uk.ASSUMPTIONS + ch.ASSUMPTIONS + [
            "Each started assignment year is costed as a full tax year (6 April to 5 April).",
        ],
    }


#summary line for tab 2
def build_summary(form, inp):
    def label(field):
        return dict(form.fields[field].choices)[form.cleaned_data[field]]

    def day(d):
        return f"{d.day} {d:%B %Y}"

    return (
        f"{label('nationality')} national, "
        f"{label('home_country')} -> {label('host_country')}, "
        f"{day(inp.start_date)} to {day(inp.end_date)}"
    )

def build_sections(route, visa):
    requirements = route["common"]["requirements"] + visa["requirements"]

    sections = []
    for key, title in SECTIONS:
        items = []
        for req in requirements:
            if req["section"] == key:
                items.append({
                    "title": req["title"],
                    "summary": req["summary"],
                    "sources": [SOURCES[k] for k in req["source"]],
                })
        sections.append({"title": title, "items": items})
    return sections

def build_timeline(route, visa, start_date):
    steps = []
    lead_weeks = 0

    for step in visa["timeline"] + route["common"]["timeline"]:
        parallel = step.get("parallel", False)
        if not parallel:
            lead_weeks += step["weeks"]

        steps.append({
            "name": step["name"],
            "duration": step["duration"],
            "parallel": parallel,
            "sources": [SOURCES[k] for k in step["source"]],
        })

    all_steps = visa["timeline"] + route["common"]["timeline"]
    return {
        "steps": steps,
        "lead_weeks": lead_weeks,
        "start_date": start_date,
        "start_by": start_date - timedelta(weeks=lead_weeks),
        "includes_licence": any(s.get("only_if_no_licence") for s in all_steps),
    }


# Create your views here.
def cost(request):
    form = EstimatorForm(request.GET if "submit" in request.GET else None)
    inputs_ok = form.is_valid()
    result = None
    if inputs_ok:
        inp = EstimatorInput.from_cleaned_data(form.cleaned_data)
        result = build_cost_result(inp)
    return render(request, "estimator/cost.html", {
        "active_tab": "cost",
        "form": form,
        "inputs_ok": inputs_ok,
        "result": result,
    })


def immigration(request):
    form = EstimatorForm(request.GET if "submit" in request.GET else None)
    inputs_ok = form.is_valid()
    result = None

    if inputs_ok:
        data = form.cleaned_data
        route = get_route(data["home_country"], data["host_country"], data["nationality"])
        if route is None:
            result = {"not_covered": True}
        else:
            inp = EstimatorInput.from_cleaned_data(data)
            visa, check = pick_visa(route, inp)

            cost_rows = build_cost_rows(route, visa, inp)


            result = {
                "summary": build_summary(form, inp),
                "eligible": check["eligible"],
                "verdict": build_verdict(visa, check, inp),
                "sections": build_sections(route, visa),
                "costs": {
                    "rows": cost_rows,
                    "total": sum(row["amount"] for row in cost_rows),
                },
                "timeline": build_timeline(route, visa, data["start_date"]),
                "assumptions": route["common"]["assumptions"] + visa["assumptions"],

            }    
         

    return render(request, "estimator/immigration.html", {
        "active_tab": "immigration",
        "form": form,
        "inputs_ok": inputs_ok,
        "result": result
        # "route": route,
                })