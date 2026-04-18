from django import forms

from .models import Student


class SrequestForm(forms.ModelForm):

    class Meta:

        model=Student
        exclude = ['user','status'] 
        fields="__all__"
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'tc_issue_date': forms.DateInput(attrs={'type': 'date'}),
            'leaving_date': forms.DateInput(attrs={'type': 'date'}),
            'declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.HiddenInput(),
            'user': forms.HiddenInput()
        }