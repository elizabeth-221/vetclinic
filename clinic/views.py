from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg  # Импорт для сложных запросов и агрегации
from django.utils import timezone  # Для работы с датами
from .models import Service, Doctor, Promotion, Review
from django.contrib import messages  # Для всплывающих сообщений
from django.views.decorators.http import require_POST  # Для ограничения метода запроса
from .forms import DoctorForm


def index(request):
    # 1. Получаем активные акции (сейчас и позже начала, и раньше окончания)
    today = timezone.now().date()
    active_promotions = Promotion.objects.filter(
        start_date__lte=today, 
        end_date__gte=today
    ).order_by('-start_date')[:3]  # Берем 3 самые свежие

    # 2. Получаем врачей для главной (с флагом is_featured)
    featured_doctors = Doctor.objects.filter(is_featured=True)[:4]

    # 3. Получаем одобренные отзывы
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')[:5]

    # 4. Обрабатываем поиск (если был поисковый запрос)
    services = Service.objects.filter(is_active=True)  # Все активные услуги для выпадающего списка или др.
    search_query = ''
    if 'q' in request.GET:  # Если в запросе есть параметр 'q' (поиск)
        search_query = request.GET['q']
        # Ищем услуги, в названии или описании которых есть искомое слово (без учета регистра)
        services = services.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # 5. Сложная бизнес-логика/агрегация: Рейтинг врачей на основе отзывов
    # Теперь это РАБОТАЕТ, т.к. связь между Doctor и Review установлена!
    doctors_with_rating = Doctor.objects.annotate(
        avg_rating=Avg('reviews__rating')  # Используем related_name='reviews'
    ).filter(
        avg_rating__isnull=False  # Исключаем врачей без отзывов
    ).order_by('-avg_rating')[:3]  # Сортируем по убыванию рейтинга и берем топ-3

    context = {
        'active_promotions': active_promotions,
        'featured_doctors': featured_doctors,
        'reviews': reviews,
        'services': services,
        'search_query': search_query,
        'doctors_with_rating': doctors_with_rating,  # Передаем в шаблон
    }
    return render(request, 'clinic/index.html', context)

def search_services(request):
    search_query = request.GET.get('q', '')
    services = Service.objects.filter(is_active=True)
    
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'search_query': search_query,
        'services': services,
        'results_count': services.count()
    }
    return render(request, 'clinic/search_results.html', context)

# CRUD для Doctor
def doctor_list(request):
    """Страница со списком всех врачей для демонстрации CRUD"""
    doctors = Doctor.objects.all().order_by('last_name', 'first_name')
    return render(request, 'clinic/doctor_list.html', {'doctors': doctors})

def doctor_detail(request, pk):
    """Детальная страница врача (Read)"""
    doctor = get_object_or_404(Doctor, pk=pk)
    # Получаем только одобренные отзывы для этого врача
    reviews = doctor.reviews.filter(is_approved=True)
    return render(request, 'clinic/doctor_detail.html', {'doctor': doctor, 'reviews': reviews})

def doctor_create(request):
    """Создание нового врача (Create)"""
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)  # request.FILES для загрузки фото
        if form.is_valid():
            new_doctor = form.save()
            messages.success(request, f'Врач {new_doctor.first_name} {new_doctor.last_name} успешно добавлен!')
            return redirect('clinic:doctor_detail', pk=new_doctor.pk)  # ← Здесь используется redirect
    else:
        form = DoctorForm()

    return render(request, 'clinic/doctor_form.html', {'form': form, 'title': 'Добавить нового врача'})

def doctor_update(request, pk):
    """Редактирование врача (Update)"""
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        # instance=doctor указывает, что мы редактируем существующий объект
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            updated_doctor = form.save()
            messages.success(request, f'Данные врача {updated_doctor.first_name} {updated_doctor.last_name} обновлены!')
            return redirect('clinic:doctor_detail', pk=doctor.pk)
    else:
        # Если запрос GET, заполняем форму данными врача
        form = DoctorForm(instance=doctor)

    return render(request, 'clinic/doctor_form.html', {'form': form, 'title': 'Редактировать врача', 'doctor': doctor})

@require_POST  # Разрешаем только POST-запросы для безопасности
def doctor_delete(request, pk):
    """Удаление врача (Delete)"""
    doctor = get_object_or_404(Doctor, pk=pk)
    full_name = f"{doctor.first_name} {doctor.last_name}"
    doctor.delete()
    messages.success(request, f'Врач {full_name} был удален.')
    return redirect('clinic:doctor_list')  # Перенаправляем обратно к списку

