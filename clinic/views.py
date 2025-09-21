from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Avg  # Импорт для сложных запросов и агрегации
from django.utils import timezone  # Для работы с датами
from .models import Service, Doctor, Promotion, Review
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

