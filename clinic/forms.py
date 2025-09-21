from django import forms
from .models import Doctor, Specialization

class DoctorForm(forms.ModelForm):
    # Это поле уже есть в модели, но мы кастомизируем виджет для удобства
    specializations = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Показывать чекбоксы
        required=False  # Необязательное поле
    )

    class Meta:
        model = Doctor
        # Перечисляем поля, которые будут в форме
        fields = ['first_name', 'last_name', 'specializations', 'experience', 'description', 'photo', 'is_featured']
        # Делаем описание необязательным для упрощения тестирования
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о враче...'}),
        }
        labels = {
            'is_featured': 'Показывать на главной',
        }