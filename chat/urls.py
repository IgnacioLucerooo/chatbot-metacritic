from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("bot/<str:nombre>/", views.index, name="bot"),
    path("bot/<str:nombre>/enviar/", views.enviar, name="enviar"),
    path("bot/<str:nombre>/reiniciar/", views.reiniciar, name="reiniciar"),
]
