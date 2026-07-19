from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('<int:pk>/edit/', views.bill_edit, name='bill_edit'),
    path('<int:pk>/delete/', views.bill_delete, name='bill_delete'),
    path('<int:pk>/toggle-paid/', views.bill_toggle_paid, name='bill_toggle_paid'),

]