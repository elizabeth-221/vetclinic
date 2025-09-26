from django.contrib import admin
from .models import Specialization, Doctor, Service, Promotion, Appointment, Review, DoctorSpecialization, ServiceDoctor
from .models import Exhibit, Hall, Guide, Tour

# Inline для врача (специализации)
class DoctorSpecializationInline(admin.TabularInline):
    model = DoctorSpecialization
    extra = 1
    verbose_name = "Специализация"
    verbose_name_plural = "Специализации"
    autocomplete_fields = ['specialization']

# Inline для специализации (врачи) - СИММЕТРИЧНАЯ СВЯЗЬ
class SpecializationDoctorInline(admin.TabularInline):
    model = DoctorSpecialization
    extra = 1
    verbose_name = "Врач с этой специализацией"
    verbose_name_plural = "Врачи с этой специализацией"
    autocomplete_fields = ['doctor']

# Inline для услуги (врачи)
class ServiceDoctorInline(admin.TabularInline):
    model = ServiceDoctor
    extra = 1
    verbose_name = "Врач услуги"
    verbose_name_plural = "Врачи, оказывающие услугу"
    autocomplete_fields = ['doctor']

# Inline для врача (услуги) - СИММЕТРИЧНАЯ СВЯЗЬ
class DoctorServiceInline(admin.TabularInline):
    model = ServiceDoctor
    extra = 1
    verbose_name = "Услуга врача"
    verbose_name_plural = "Услуги врача"
    autocomplete_fields = ['service']

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'doctors_count')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = (SpecializationDoctorInline,)  # СИММЕТРИЧНАЯ СВЯЗЬ
    
    @admin.display(description="Кол-во врачей")
    def doctors_count(self, obj):
        return obj.doctor_set.count()

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('photo_preview', 'full_name', 'experience_display', 'is_featured', 'specializations_list')
    list_display_links = ('full_name',)
    list_filter = ('is_featured', 'specializations')
    list_editable = ('is_featured',)
    search_fields = ('first_name', 'last_name')
    inlines = (DoctorSpecializationInline, DoctorServiceInline)  # СИММЕТРИЧНАЯ СВЯЗЬ
    
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'photo', 'is_featured')
        }),
        ('Профессиональная информация', {
            'fields': ('experience', 'description'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description="Фото")
    def photo_preview(self, obj):
        from django.utils.html import format_html
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.photo.url)
        return "—"

    @admin.display(description="Опыт (лет)")
    def experience_display(self, obj):
        return f"{obj.experience} г."

    @admin.display(description="Специализации")
    def specializations_list(self, obj):
        return ", ".join([spec.name for spec in obj.specializations.all()])

    @admin.display(description="Имя врача")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'doctors_count')
    list_display_links = ('name',)
    list_filter = ('is_active',)
    list_editable = ('price', 'is_active')
    search_fields = ('name', 'description')
    exclude = ('doctors',)
    inlines = (ServiceDoctorInline,)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'is_active')
        }),
        ('Описание', {
            'fields': ('description', 'image')
        }),
    )

    @admin.display(description="Кол-во врачей")
    def doctors_count(self, obj):
        return obj.doctors.count()

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    list_display_links = ('title',)
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'text')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'image')
        }),
        ('Содержание и даты', {
            'fields': ('text', 'start_date', 'end_date')
        }),
    )

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
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('service',)
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('client_name', 'phone', 'email')
        }),
        ('Информация о питомце и услуге', {
            'fields': ('pet_name', 'service', 'desired_date')
        }),
        ('Дополнительная информация', {
            'fields': ('message', 'status', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'doctor', 'rating', 'is_approved', 'short_text', 'created_at')
    list_display_links = ('author_name',)
    list_filter = ('rating', 'is_approved', 'created_at', 'doctor')
    list_editable = ('is_approved',)
    search_fields = ('author_name', 'text', 'doctor__first_name', 'doctor__last_name')
    readonly_fields = ('created_at',)
    raw_id_fields = ('doctor',)
    actions = ['approve_reviews']
    
    fieldsets = (
        (None, {
            'fields': ('author_name', 'doctor', 'rating', 'is_approved')
        }),
        ('Содержание отзыва', {
            'fields': ('text',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description="Текст отзыва")
    def short_text(self, obj):
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text

    @admin.action(description="Одобрить выбранные отзывы")
    def approve_reviews(self, request, queryset):
        updated_count = queryset.update(is_approved=True)
        self.message_user(request, f"{updated_count} отзыв(ов) было одобрено.")



@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
    list_display = ['name', 'era', 'country', 'current_hall']
    list_filter = ['era', 'country']
    search_fields = ['name', 'description']

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ['name', 'theme', 'floor']
    list_filter = ['theme', 'floor']
    search_fields = ['name', 'theme']

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'experience']
    list_filter = ['specialization']
    search_fields = ['full_name', 'specialization']
    filter_horizontal = ['guided_halls']  # Пункт 3 - удобное M2M

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['theme', 'datetime', 'max_visitors', 'guide', 'is_public']
    list_filter = ['is_public', 'datetime']  # Пункт 4 и 5 - фильтры
    search_fields = ['theme', 'guide__full_name']  # Пункт 1 - поиск
    date_hierarchy = 'datetime'  # Пункт 2 - поиск по дате
    filter_horizontal = ['thematic_exhibits']  # Пункт 3 - удобное M2M