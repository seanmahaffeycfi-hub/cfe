from django.urls import path
from . import views

urlpatterns = [
    path('', views.cashflow_view, name='cashflow_view'),
]