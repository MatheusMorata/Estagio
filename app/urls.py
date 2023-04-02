from django.contrib import admin
from django.urls import path
from projeto.views import home

urlpatterns = [
    path('home/',home),
]
