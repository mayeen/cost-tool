from decimal import Decimal
from datetime import timedelta
from .calculations.inputs import EstimatorInput
from .calculations.immigration import build_verdict, pick_visa, build_cost_rows

from django.shortcuts import render
from django.http import HttpResponse

from estimator.rules.immigration import SOURCES, get_route
from .forms import EstimatorForm
from .calculations.cost import add_totals



SECTIONS = [
    ("work_permit", "Work permit"),
    ("business_visit", "Business visit before the assignment"),
    ("passport", "Passport"),
    ("employer_duty", "Employer duty"),
]
def dummy_cost_result():
    """DUMMY figures (from my research notes): steps 21-25 replace this with real logic."""
    d = Decimal
    sections = [
        {
            "title": "1. Home pay",
            "subtotal_label": "Home pay",
            "rows": [
                {"name": "Base salary", "tag": "", "amounts": [d("136363.64"), d("136363.64")], "sources": []},
                {"name": "Bonus", "tag": "", "amounts": [d("18181.82"), d("18181.82")], "sources": []},
            ],
        },
        {
            "title": "2. Assignment benefits",
            "subtotal_label": "Assignment benefits",
            "rows": [
                {"name": "Housing in London", "tag": "Taxable benefit in kind", "amounts": [d("36000"), d("36000")], "sources": []},
                {"name": "Relocation allowance", "tag": "Taxable cash", "amounts": [d("4545.45"), None], "sources": []},
                {"name": "Moving costs", "tag": "Not taxable in the UK", "amounts": [d("6000"), None], "sources": []},
                {"name": "Temporary housing", "tag": "Taxable benefit in kind", "amounts": [d("4000"), None], "sources": []},
            ],
        },
        {
            "title": "3. Host tax and charges paid by the employer",
            "subtotal_label": "Host tax and charges",
            "rows": [
                {"name": "UK income tax, including tax on tax", "tag": "Grossed up, see working below", "amounts": [d("107892.74"), d("100901.01")], "sources": []},
                {"name": "UK employer National Insurance", "tag": "Swiss system applies, see below", "amounts": [d("0"), d("0")], "sources": []},
            ],
        },
        {
            "title": "4. Deductions",
            "subtotal_label": "Deductions",
            "subtract": True,
            "rows": [
                {"name": "Hypothetical Swiss income tax", "tag": "Federal, cantonal and communal", "amounts": [d("26889.09"), d("26889.09")], "sources": []},
                {"name": "Hypothetical Swiss social security", "tag": "AHV/IV/EO and unemployment insurance", "amounts": [d("9672.91"), d("9672.91")], "sources": []},
            ],
        },
    ]
    return {
        "years": ["Year 1 (2026/27)", "Year 2 (2027/28)"],
        "sections": sections,
        "totals": add_totals(sections),
        "social_security": {
            "title": "Social security: Swiss system applies",
            "text": (
                "The employee works for a Swiss employer and is sent to the UK temporarily, "
                "for up to 2 years. With a certificate of coverage from Switzerland, only Swiss "
                "contributions are paid, so no UK National Insurance is due for the employee "
                "or the employer."
            ),
            "sources": [{
                "title": "GOV.UK: Social security contributions for workers coming to the UK from the EEA or Switzerland",
                "url": "https://www.gov.uk/guidance/social-security-contributions-for-workers-coming-to-the-uk-from-the-eea-or-switzerland",
            }],
        },
        "working": [
            {
                "year": "Year 1 (2026/27)",
                "start_income": d("162528.91"),
                "rounds": [
                    {"number": 1, "income": d("162528.91"), "tax": d("59341.01")},
                    {"number": 2, "income": d("221869.92"), "tax": d("86044.46")},
                    {"number": 3, "income": d("248573.37"), "tax": d("98061.02")},
                    {"number": 4, "income": d("260589.93"), "tax": d("103468.47")},
                ],
                "round_count": 23,
                "final": {"income": d("270421.65"), "tax": d("107892.74")},
            },
            {
                "year": "Year 2 (2027/28)",
                "start_income": d("153983.45"),
                "rounds": [
                    {"number": 1, "income": d("153983.45"), "tax": d("55495.55")},
                    {"number": 2, "income": d("209479.00"), "tax": d("80468.55")},
                    {"number": 3, "income": d("234452.00"), "tax": d("91706.40")},
                    {"number": 4, "income": d("245689.85"), "tax": d("96763.44")},
                ],
                "round_count": 23,
                "final": {"income": d("254884.46"), "tax": d("100901.01")},
            },
        ],
        "assumptions": [
            "Hypothetical Swiss income tax is the Swiss Federal Tax Administration calculator "
            "result for CHF 170,000 in the city of Zurich, single, no children, no church tax.",
            "UK 2026/27 rates are used for both years. The employee is UK tax resident in both years.",
            "Moving costs are within the £8,000 relocation exemption. Temporary housing is treated "
            "as taxable.",
            "Swiss employer social security contributions are not included.",
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
    result = dummy_cost_result() if inputs_ok else None
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