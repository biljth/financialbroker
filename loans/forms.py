from django import forms
from .models import LoanInquiry

class LoanInquiryForm(forms.ModelForm):
    class Meta:
        model = LoanInquiry
        fields = ['name', 'phone_number', 'email', 'domicile', 'loan_amount', 'loan_type', 'gender']
        widgets = {
            'loan_type': forms.HiddenInput(),
            'loan_amount': forms.TextInput(attrs={'class': 'loan-amount'})
        }
        
class HistoryForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)