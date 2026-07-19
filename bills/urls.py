from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('<int:pk>/delete/', views.bill_delete, name='bill_delete'),
]