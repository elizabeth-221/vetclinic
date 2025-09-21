from django.urls import path
from . import views

urlpatterns = [
    # пока можно оставить пустым или добавить временный путь
    path('', views.index, name='index'),
]