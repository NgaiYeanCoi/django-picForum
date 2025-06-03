from django import forms
from .models import Work

class WorkForm(forms.ModelForm):
    """作品表单"""
    class Meta:
        model = Work
        fields = ['title', 'description', 'image', 'shot_date', 'camera_model', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'shot_date': forms.DateInput(attrs={'type': 'date'}),
        }    