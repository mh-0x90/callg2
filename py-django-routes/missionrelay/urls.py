from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.urls import path

from missions.registry import urlpatterns
from missions.views import home, logout_view


urlpatterns = [
    path("", home, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
] + urlpatterns