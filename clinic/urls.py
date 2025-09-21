from django.urls import path
from . import views

app_name = 'clinic'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_services, name='search_services'),
    # Новые маршруты для CRUD врачей:
    path('doctors/', views.doctor_list, name='doctor_list'),  # Список всех врачей
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),  # Просмотр одного
    path('doctor/new/', views.doctor_create, name='doctor_create'),  # Создание
    path('doctor/<int:pk>/edit/', views.doctor_update, name='doctor_update'),  # Редактирование
    path('doctor/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),  # Удаление
]