# complaints/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Complaint, Category, StudentLevel, StudentLevelType

class ComplaintForm(forms.ModelForm):
    # Add fields for Student Level and Student Level Type
    student_level = forms.ModelChoiceField(queryset=StudentLevel.objects.all())
    student_level_type = forms.ModelChoiceField(queryset=StudentLevelType.objects.all())
    phone_number = forms.CharField(label='Phone Number', max_length=15)  # Add the phone_number field

    class Meta:
        model = Complaint
        fields = ['name', 'student_id','phone_number', 'student_level', 'student_level_type', 'category', 'description', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit Complaint'))
