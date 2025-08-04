from django import forms
from .models import LoanInquiry, Property, PropertyInquiry, AdsInquiry

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

class PropertySearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search by title'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Location'}))
    min_area = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min Area (Sqft)'}))
    max_area = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Max Area (Sqft)'}))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min Price'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Max Price'}))


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'location', 'property_type', 'property_category', 'area_surface', 'area_building', 'bedrooms', 'bathrooms']
        widgets = {
            'price': forms.TextInput(attrs={'class': 'price'})
        }

class PropertyInquiryForm(forms.ModelForm):
    class Meta:
        model = PropertyInquiry
        fields = ['name', 'phone_number', 'email']

class AdsForm(forms.ModelForm):
    class Meta:
        model = AdsInquiry
        fields = ['name', 'phone_number', 'email']


class KPRCalculatorForm(forms.Form):
    harga_properti = forms.CharField(
        label='Harga Properti',
        widget=forms.TextInput(attrs={'class': 'loan-amount form-control'})
    )
    uang_muka = forms.CharField(
        label='Uang Muka',
        widget=forms.TextInput(attrs={'class': 'loan-amount form-control'})
    )
    bunga = forms.FloatField(
        label='Suku Bunga',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    tenor = forms.IntegerField(
        label='Tenor',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class ModalKerjaCalculatorForm(forms.Form):
    plafon_pinjaman = forms.CharField(
        label='Plafon Pinjaman',
        widget=forms.TextInput(attrs={'class': 'loan-amount form-control'})
    )
    bunga = forms.FloatField(
        label='Suku Bunga',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    tenor = forms.IntegerField(
        label='Tenor (dalam tahun)',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class MultigunaCalculatorForm(forms.Form):
    plafon_pinjaman = forms.CharField(
        label='Plafon Pinjaman',
        widget=forms.TextInput(attrs={'class': 'loan-amount form-control'})
    )
    bunga = forms.FloatField(
        label='Suku Bunga',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    tenor = forms.IntegerField(
        label='Tenor (dalam tahun)',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
