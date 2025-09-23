from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import Service, Doctor, Promotion, Review
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import DoctorForm


def index(request):
    # 1. Получаем активные акции
    today = timezone.now().date()
    active_promotions = Promotion.objects.filter(
        start_date__lte=today, 
        end_date__gte=today
    ).order_by('-start_date')[:3]

    # 2. УБИРАЕМ featured_doctors - оставляем ТОЛЬКО врачей с лучшими отзывами
    doctors_with_rating = Doctor.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    ).filter(
        avg_rating__isnull=False,
        reviews_count__gte=1
    ).order_by('-avg_rating')[:3]  # Берем топ-3 врача по рейтингу

    # 3. Получаем одобренные отзывы
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')[:5]

    # 4. Обрабатываем поиск
    services = Service.objects.filter(is_active=True)
    search_query = ''
    if 'q' in request.GET:
        search_query = request.GET['q']
        services = services.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    context = {
        'active_promotions': active_promotions,
        'doctors': doctors_with_rating,  # Переименовываем для ясности
        'reviews': reviews,
        'services': services,
        'search_query': search_query,
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
    doctors = Doctor.objects.all().order_by('last_name', 'first_name')
    return render(request, 'clinic/doctor_list.html', {'doctors': doctors})

def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    reviews = doctor.reviews.filter(is_approved=True)
    return render(request, 'clinic/doctor_detail.html', {'doctor': doctor, 'reviews': reviews})

def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            new_doctor = form.save()
            messages.success(request, f'Врач {new_doctor.first_name} {new_doctor.last_name} успешно добавлен!')
            return redirect('clinic:doctor_detail', pk=new_doctor.pk)
    else:
        form = DoctorForm()

    return render(request, 'clinic/doctor_form.html', {'form': form, 'title': 'Добавить нового врача'})

def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            updated_doctor = form.save()
            messages.success(request, f'Данные врача {updated_doctor.first_name} {updated_doctor.last_name} обновлены!')
            return redirect('clinic:doctor_detail', pk=doctor.pk)
    else:
        form = DoctorForm(instance=doctor)

    return render(request, 'clinic/doctor_form.html', {'form': form, 'title': 'Редактировать врача', 'doctor': doctor})

@require_POST
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    full_name = f"{doctor.first_name} {doctor.last_name}"
    doctor.delete()
    messages.success(request, f'Врач {full_name} был удален.')
    return redirect('clinic:doctor_list')