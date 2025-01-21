from django.db import models
from django.utils.text import slugify

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

class Property(models.Model):
    PROPERTY_TYPES = [
        ('rent', 'For Rent'),
        ('sell', 'For Sale'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES)
    area = models.IntegerField(null=True, blank=True)  # Optional
    bedrooms = models.IntegerField(null=True, blank=True)  # Optional
    bathrooms = models.IntegerField(null=True, blank=True) 
    image = models.ImageField(upload_to='property_images/')
    slug = models.SlugField(unique=True, blank=True)  # Add slug field
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.id}")  # Automatically generate slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
class PropertyInquiry(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name}"
    
class AdsInquiry(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name}"