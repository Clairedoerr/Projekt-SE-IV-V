from django.urls import path
from meine_app import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("registrieren/", views.registrieren, name="registrieren"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profil/", views.profil, name="profil"),
    path("wasser/", views.wasser, name="wasser"),
    path("sensor/", views.sensor, name="sensor"),
    path("giessen/", views.giessen, name="giessen"),
]

urlpatterns += staticfiles_urlpatterns()
































































  





