from django.shortcuts import render
from django.http import HttpResponse
from .forms import ImmigrationForm

# Create your views here.
def cost(request):
    return render(request, 'estimator/cost.html', {'active_tab': 'cost'})

def immigration(request):
    route = None

    if "submit" in request.GET:
        immigration_form = ImmigrationForm(request.GET)
        if immigration_form.is_valid():
            data = immigration_form.cleaned_data
            route = f"{data['home_country']} → {data['host_country']}"
    else:
        immigration_form = ImmigrationForm()
    return render(request, 'estimator/immigration.html', 
                  {'active_tab': 'immigration',
                   'form': immigration_form,
                   'route': route
                  })