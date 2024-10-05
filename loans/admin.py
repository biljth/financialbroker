from django.contrib import admin
from .models import LoanInquiry

@admin.register(LoanInquiry)
class LoanInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'loan_type', 'submitted_at') 
