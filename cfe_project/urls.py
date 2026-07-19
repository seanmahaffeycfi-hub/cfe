from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', RedirectView.as_view(url='/income/', permanent=False)),
    path('income/', include('income.urls')),
    path('bills/', include('bills.urls')),
    path('cashflow/', include('cashflow.urls')),
    path('account/', include('accounts.urls')),
]