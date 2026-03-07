from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from finance import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # App pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='finance/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Finance section (give it a prefix so it doesn't clash with home)
    path('finance/', include('finance.urls')),
]