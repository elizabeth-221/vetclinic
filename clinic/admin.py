from django.contrib import admin
from .models import Specialization, Doctor, Service, Promotion, Appointment, Review

# 1. Класс для настройки отображения связанных объектов "внутри" другого объекта (Inlines)
class DoctorSpecializationInline(admin.TabularInline):
    model = Doctor.specializations.through  # Указываем промежуточную модель для связи M2M
    extra = 1  # Количество пустых форм для добавления новых связей
    verbose_name = "Специализация"
    verbose_name_plural = "Специализации"

class ServiceDoctorsInline(admin.TabularInline):
    model = Service.doctors.through  # Промежуточная модель для связи Услуга-Врачи
    extra = 1
    verbose_name = "Врач"
    verbose_name_plural = "Врачи, оказывающие услугу"

# 2. Классы ModelAdmin для каждой модели
@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Что показывать в списке
    list_display_links = ('id', 'name')  # По каким полям можно кликнуть для редактирования
    search_fields = ('name',)  # По каким полям работает поиск
    ordering = ('name',)  # Сортировка по умолчанию

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    # Настройка отображения списка врачей
    list_display = ('photo_preview', 'full_name', 'experience_display', 'is_featured', 'specializations_list')
    list_display_links = ('full_name',)  # Кликабельно только полное имя
    list_filter = ('is_featured', 'specializations')  # Фильтры сбоку
    list_editable = ('is_featured',)  # Можно менять галочку "на главной" прямо из списка
    search_fields = ('first_name', 'last_name')  # Поиск по имени и фамилии
    filter_horizontal = ('specializations',)  # Красивый виджет для выбора специализаций
    # Исключаем поле, которое уже отображено через inline
    exclude = ('specializations',)
    # Подключаем наш inline-класс
    inlines = (DoctorSpecializationInline,)
    # Для удобства выбора услуг (если решим добавить и их тоже через filter_horizontal)
    # raw_id_fields = ('services',) # Раскомментировать, если будет много услуг

    # Кастомный метод для отображения фото в списке (маленькая превьюшка)
    @admin.display(description="Фото")
    def photo_preview(self, obj):
        from django.utils.html import format_html
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.photo.url)
        return "—"

    # Кастомный метод для красивого отображения опыта
    @admin.display(description="Опыт (лет)")
    def experience_display(self, obj):
        return f"{obj.experience} г."

    # Кастомный метод для отображения всех специализаций в одной строке
    @admin.display(description="Специализации")
    def specializations_list(self, obj):
        return ", ".join([spec.name for spec in obj.specializations.all()])

    # Кастомный метод для отображения полного имени
    @admin.display(description="Имя врача")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'doctors_count')
    list_display_links = ('name',)
    list_filter = ('is_active',)
    list_editable = ('price', 'is_active')  # Цену и активность можно менять в списке
    search_fields = ('name', 'description')
    # Красивый виджет для выбора врачей (т.к. связь M2M)
    filter_horizontal = ('doctors',)
    # Показываем связанных врачей прямо на странице услуги
    inlines = (ServiceDoctorsInline,)

    # Кастомный метод для подсчета числа врачей
    @admin.display(description="Кол-во врачей")
    def doctors_count(self, obj):
        return obj.doctors.count()

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    list_display_links = ('title',)
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'text')
    date_hierarchy = 'start_date'  # Иерархическая навигация по датам сверху

    # Вычисляемое поле: активна ли акция сейчас?
    @admin.display(description="Активна?", boolean=True)
    def is_active(self, obj):
        from django.utils import timezone
        now = timezone.now().date()
        return obj.start_date <= now <= obj.end_date

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'phone', 'pet_name', 'service', 'desired_date', 'status', 'created_at')
    list_display_links = ('client_name',)
    list_filter = ('status', 'service', 'created_at', 'desired_date')
    search_fields = ('client_name', 'phone', 'pet_name', 'service__name')
    list_editable = ('status',)  # Статус можно менять прямо в списке!
    readonly_fields = ('created_at',)  # Дату создания нельзя редактировать
    date_hierarchy = 'created_at'  # Навигация по дате создания заявки
    # Показывать сырой ID для услуги (удобно, если услуг тысячи)
    raw_id_fields = ('service',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'doctor', 'rating', 'is_approved', 'short_text', 'created_at')  # Добавили 'doctor'
    list_display_links = ('author_name',)
    list_filter = ('rating', 'is_approved', 'created_at', 'doctor')  # Добавили фильтр по врачу
    list_editable = ('is_approved',)
    search_fields = ('author_name', 'text', 'doctor__first_name', 'doctor__last_name')  # Добавили поиск по врачу
    readonly_fields = ('created_at',)
    # Добавляем поле врача в сырой виджет (удобно, если врачей много)
    raw_id_fields = ('doctor',) 
    actions = ['approve_reviews']

    @admin.display(description="Текст отзыва")
    def short_text(self, obj):
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text

    @admin.action(description="Одобрить выбранные отзывы")
    def approve_reviews(self, request, queryset):
        updated_count = queryset.update(is_approved=True)
        self.message_user(request, f"{updated_count} отзыв(ов) было одобрено.")