from django.urls import path
from . import views

urlpatterns = [
    path("", views.cost, name="cost"),
    path("immigration/", views.immigration, name="immigration"),    
]