from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("article/<int:article_id>", views.detail, name="detail"),
    path("home/", views.home, name="home"),
]