from django.urls import path
from . import views

urlpatterns = [
    path('', views.cashflow_view, name='cashflow_view'),
    path('by-account/', views.cashflow_by_account_view, name='cashflow_by_account'),

]