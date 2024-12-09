from django import forms
from staff.models import Staff
from .models import Service

class ServiceForm(forms.ModelForm):
    staffs = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Assign Staff"
    )

    class Meta:
        model = Service
        fields = [
            'name', 'description', 'price', 'duration_minutes', 
            'start_time', 'end_time', 'department', 'status'
        ]


