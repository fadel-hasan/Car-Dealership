from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


class CarManager(models.Manager):
    def total_cars(self):
        return self.count()

    def sold_cars(self):
        return self.filter(sold=True).count()

    def active_cars(self):
        return self.filter(sold=False).count()
    
    def cars_by_brand(self):
        return self.values('brand').annotate(count=Count('id')).order_by('-count')
    
    def recent_sales(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return self.filter(
            sold=True,
            created_at__gte=thirty_days_ago
        ).count()
    
class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    car_images = models.JSONField()  # Store multiple image paths
    description = models.TextField()
    sold = models.BooleanField(default=False)
    color = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CarManager()
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class ComplaintManager(models.Manager):
    def total_complaints(self):
        return self.count()
    def comlaints_by_status(self):
        return self.values('status').annotate(count=Count('id')).order_by('status')
      
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date = models.DateTimeField(auto_now_add=True)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True)

    objects = ComplaintManager()
    
    def __str__(self):
        return f"Complaint by {self.name}"

class AdManager(models.Manager):
    def active_ads(self):
        return self.filter(end_date__gte=timezone.now()).count()
    
    
class Ad(models.Model):
    STATUS_CHOICES = [
        ('home_top', 'Home_Top'),
        ('home_bottom', 'Home_Bottom'),
        ('sidebar', 'Sidebar'),
    ]
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ads/')
    url = models.URLField()
    hit = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location_ad = models.CharField(max_length=20,choices=STATUS_CHOICES)

    objects = AdManager()
    def __str__(self):
        return self.name

class Setting(models.Model):
    site_name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='site/')
    favicon = models.ImageField(upload_to='site/')
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    facebook = models.URLField(blank=True,null=True)
    whatsapp = models.CharField(max_length=20, blank=True,null=True)
    instagram = models.URLField(blank=True,null=True)
    home_images = models.TextField(help_text="Comma separated list of image paths")
    home_words = models.TextField(help_text="Comma separated list of words for homepage")

    def __str__(self):
        return self.site_name
    
    def get_home_images_list(self):
        """Returns home_images as a list of image paths, limited to 3"""
        if not self.home_images:
            return []
        images = [img.strip() for img in self.home_images.split(',') if img.strip()]
        return images[:3]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def has_profile_photo(self):
        return bool(self.profile_photo and self.profile_photo.name)

    @property
    def profile_picture_url(self):
        if self.has_profile_photo:
            return self.profile_photo.url
        return None

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            mobile_number='', 
            city='Unknown',            
            country='Unknown',       
            email_verified=False)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()