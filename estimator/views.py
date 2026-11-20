from django.shortcuts import render
from django.http import HttpResponse
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
        data = form.cleaned_data
        route = f"{data['home_country']} > {data['host_country']}"

    return render(request, "estimator/immigration.html", {
        "active_tab": "immigration",
        "form": form,
        "inputs_ok": inputs_ok,
        "route": route,
                  })