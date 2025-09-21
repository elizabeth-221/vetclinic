from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clinic.urls')), # Подключим будущие URL-адреса приложения clinic
]

# Эта строка добавляет маршрутизацию для медиа-файлов только в режиме отладки (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)