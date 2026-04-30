from django import forms
from .models import Booking
from django.utils import timezone

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'check_in', 'check_out', 'guests', 'special_requests']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+212 6XX XXX XXX'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Nom complet', 'email': 'Email', 'phone': 'Téléphone',
            'check_in': "Date d'arrivée", 'check_out': 'Date de départ',
            'guests': 'Personnes', 'special_requests': 'Demandes spéciales',
        }

    def __init__(self, *args, room=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = room
        today = timezone.now().date().isoformat()
        self.fields['check_in'].widget.attrs['min'] = today
        self.fields['check_out'].widget.attrs['min'] = today
        if room:
            self.fields['guests'].widget.attrs['max'] = room.capacity

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        if check_in and check_out:
            if check_in >= check_out:
                raise forms.ValidationError("La date de départ doit être après la date d'arrivée.")
            if check_in < timezone.now().date():
                raise forms.ValidationError("La date d'arrivée ne peut pas être dans le passé.")
        return cleaned_data

class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': 'form-select form-select-sm'})}
