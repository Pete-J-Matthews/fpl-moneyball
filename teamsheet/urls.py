from django.urls import path
from . import views

app_name = 'teamsheet'

urlpatterns = [
    path('', views.teamsheet, name='teamsheet'),
]