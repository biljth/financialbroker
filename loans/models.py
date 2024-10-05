from django.db import models

class LoanInquiry(models.Model):
    GENDER_CHOICES = [
        ('male', 'Laki-laki'),
        ('female', 'Perempuan'),
    ]
    
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    domicile = models.CharField(max_length=100)
    loan_amount = models.CharField(max_length=100)
    loan_type = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.loan_type}"