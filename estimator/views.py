from decimal import Decimal
from datetime import timedelta
from .calculations.inputs import EstimatorInput
from .calculations.immigration import build_verdict, pick_visa

from django.shortcuts import render
from django.http import HttpResponse

from estimator.rules.immigration import SOURCES, get_route
from .forms import EstimatorForm


SECTIONS = [
    ("work_permit", "Work permit"),
    ("business_visit", "Business visit before the assignment"),
    ("passport", "Passport"),
    ("employer_duty", "Employer duty"),
]

BASIS_TEXT = {
    "one_off": "One-off",
    "visa_length": "Depends on visa length",
    "per_year_half_bands": "Per year of visa",
    "first_12_then_6": "First 12 months, then per 6 months",
}

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

def build_cost_rows(route, visa):
    rows = []
    for cost in route["common"]["costs"] + visa["costs"]:
        rows.append({
            "name": cost["name"],
            "basis": BASIS_TEXT[cost["basis"]],
            "amount": Decimal("100"),  
            "sources": [SOURCES[k] for k in cost["source"]],
        })
    return rows

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

    return render(request, "estimator/cost.html", {
        "active_tab": "cost",
        "form": form,
        "inputs_ok": inputs_ok,
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

            cost_rows = build_cost_rows(route, visa)


            # dummy data
            result = {
                "summary": "Swiss national, Switzerland -> United Kingdom, 1 Jan 2026 to 31 Dec 2027",
                "verdict": build_verdict(visa, check, inp),
                "sections": build_sections(route, visa),
                "costs": {
                    "rows": cost_rows,
                    "total": sum(row["amount"] for row in cost_rows),
                },
                "timeline": build_timeline(route, visa, data["start_date"]),



            }
         

    return render(request, "estimator/immigration.html", {
        "active_tab": "immigration",
        "form": form,
        "inputs_ok": inputs_ok,
        "result": result
        # "route": route,
                  })