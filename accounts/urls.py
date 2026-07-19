from django.urls import path
from . import views

urlpatterns = [
    path('export/', views.export_data, name='export_data'),
]