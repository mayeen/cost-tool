from django.shortcuts import render
from django.http import HttpResponse

from estimator.rules.immigration import SOURCES
from .forms import EstimatorForm

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
    route = None

    if inputs_ok:
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