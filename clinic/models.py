from django.db import models

# Модель для специализаций врачей (Справочник)
class Specialization(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название специализации")

    class Meta:
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"

    def __str__(self):
        return self.name

# Модель для врачей
class Doctor(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    specializations = models.ManyToManyField(
        Specialization, 
        through='DoctorSpecialization',
        verbose_name="Специализации"
    )
    experience = models.PositiveIntegerField(verbose_name="Опыт работы (лет)")
    description = models.TextField(verbose_name="Информация о враче", blank=True)
    photo = models.ImageField(upload_to='doctors/', verbose_name="Фотография", blank=True)
    is_featured = models.BooleanField(default=False, verbose_name="Показывать на главной")

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Промежуточная модель для связи врачей и специализаций
class DoctorSpecialization(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="Врач")
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, verbose_name="Специализация")
    
    class Meta:
        verbose_name = "Специализация врача"
        verbose_name_plural = "Специализации врачей"
        db_table = 'clinic_doctor_specializations'

    def __str__(self):
        return f"{self.doctor} - {self.specialization}"

# Модель для услуг
class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    image = models.ImageField(upload_to='services/', verbose_name="Изображение", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    doctors = models.ManyToManyField(
        Doctor, 
        through='ServiceDoctor',
        verbose_name="Врачи", 
        blank=True
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.name

# Промежуточная модель для связи Услуги-Врачи
class ServiceDoctor(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="Врач")
    
    class Meta:
        verbose_name = "Врач услуги"
        verbose_name_plural = "Врачи услуг"
        db_table = 'clinic_service_doctors'
        unique_together = ['service', 'doctor']

    def __str__(self):
        return f"{self.service.name} - {self.doctor.first_name} {self.doctor.last_name}"

# Модель для акций
class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок акции")
    text = models.TextField(verbose_name="Текст акции")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    image = models.ImageField(upload_to='promotions/', verbose_name="Изображение", blank=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['-start_date']

    def __str__(self):
        return self.title

# Модель для заявок на запись
class Appointment(models.Model):
    STATUS_NEW = 'new'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_CONFIRMED, 'Подтверждена'),
        (STATUS_CANCELED, 'Отменена'),
    ]

    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email", blank=True)
    pet_name = models.CharField(max_length=100, verbose_name="Кличка питомца")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    desired_date = models.DateField(verbose_name="Желаемая дата")
    message = models.TextField(verbose_name="Дополнительная информация", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заявка на запись"
        verbose_name_plural = "Заявки на запись"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка от {self.client_name} ({self.service})"

# Модель для отзывов
class Review(models.Model):
    author_name = models.CharField(max_length=100, verbose_name="Имя автора")
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveIntegerField(verbose_name="Оценка", choices=((1,1), (2,2), (3,3), (4,4), (5,5)))
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Врач",
        related_name='reviews'
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.author_name} ({self.rating}/5)"