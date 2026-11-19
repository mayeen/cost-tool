from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def cost(request):
    return render(request, 'estimator/cost.html')

def immigration(request):
    return render(request, 'estimator/immigration.html')