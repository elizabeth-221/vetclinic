from django.urls import path
from . import views

app_name = 'clinic'

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
]