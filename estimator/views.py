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
            visa = route["visas"][0]

        # dummy data
        result = {
            "summary": "Swiss national, Switzerland -> United Kingdom, 1 Jan 2026 to 31 Dec 2027",
            "verdict": {
                "title": "Work visa needed: Senior or Specialist Worker visa (Global Business Mobility)",
                "checks": [
                    {
                        "label": "Salary check",
                        "text": "£100,000 a year. Needs at least £52,500 or the job's going rate, whichever is higher.",
                    },
                    {
                        "label": "Time with employer",
                        "text": "5 years. Needs 12 months when earning under £73,900; none at £73,900 or more.",
                    },
                ],
                "sources": [SOURCES["ssw_eligibility"]],
            },
            "sections": build_sections(route, visa),

        }
        # data = form.cleaned_data
        # route = f"{data['home_country']} > {data['host_country']}"

    return render(request, "estimator/immigration.html", {
        "active_tab": "immigration",
        "form": form,
        "inputs_ok": inputs_ok,
        "result": result
        # "route": route,
                  })