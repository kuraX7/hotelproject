from django import forms
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'category', 'status', 'description', 'price', 'capacity', 'size',
                  'has_wifi', 'has_ac', 'has_balcony', 'has_sea_view', 'has_tv', 'has_minibar', 'has_safe', 'has_bathtub',
                  'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Suite Royale Atlas'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'min': 0}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'size': forms.NumberInput(attrs={'class': 'form-control', 'min': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nom', 'category': 'Catégorie', 'status': 'Statut',
            'description': 'Description', 'price': 'Prix/nuit (MAD)',
            'capacity': 'Capacité (pers.)', 'size': 'Superficie (m²)',
            'has_wifi': 'WiFi', 'has_ac': 'Climatisation', 'has_balcony': 'Balcon',
            'has_sea_view': 'Vue mer', 'has_tv': 'TV', 'has_minibar': 'Mini-bar',
            'has_safe': 'Coffre-fort', 'has_bathtub': 'Baignoire', 'image': 'Image principale',
        }
