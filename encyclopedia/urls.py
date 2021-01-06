from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>/", views.entry, name="entry"),
    path("newpage/", views.newpage, name="newpage"),
    path("<str:title>/edit/", views.edit, name="edit"),
    path("search/", views.search, name="search"),
    path("random/", views.random, name="random")
]
