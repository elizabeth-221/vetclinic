from django.urls import path
from . import views

app_name = 'clinic'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_services, name='search_services'),  # Новая строка
    
]