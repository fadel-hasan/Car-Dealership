from django.contrib import admin
from .models import Car, Complaint, Ad, Setting
from django.utils.html import format_html
from django.urls import path,reverse
from . import admin_views
from .admin_views import *
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django import forms

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_view(admin_statistics), name='statistics'),
            path('complaints/', self.admin_view(manage_complaints), name='complaints'),
            path('complaints/<int:complaint_id>/update/', self.admin_view(update_complaint), name='update_complaint'),
            path('complaints/<int:complaint_id>/reject/', self.admin_view(reject_complaint), name='reject_complaint'),
            path("complaints/<int:complaint_id>/toggle-public/", self.admin_view(toggle_public_complaint), name="toggle_public_complaint"),
        ]
        
        return custom_urls + urls
    
    # def admin_index(self, request):
    #     return HttpResponseRedirect(reverse('myadmin:   admin-stats'))

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        
        if app_label is None:
            app_list.append(
                {
                    'name': 'Management',
                    'app_label': 'management',
                    'app_url': '#',
                    'models': [
                        {
                            'name': 'Statistics',
                            'object_name': 'statistics',
                            'admin_url': reverse('admin:statistics'),
                            'view_only': True,
                        },
                        {
                            'name': 'Complaints',
                            'object_name': 'complaints',
                            'admin_url': reverse('admin:complaints'),
                            'view_only': True,
                        }
                    ],
                }
            )
        return app_list
admin_site = CustomAdminSite(name='myadmin')

admin_site.register(User)
admin_site.register(Group)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'price', 'user', 'sold', 'city', 'display_images')
    list_filter = ('brand', 'sold', 'city', 'country')
    search_fields = ('brand', 'model', 'description')
    
    def display_images(self, obj):
        if obj.car_images:
            html = ''
            for img_url in obj.car_images[:3]:
                html += f'<img src="{img_url}" style="width: 50px; height: 50px; margin-right: 5px;" />'
            return format_html(html)
        return '-'
    
    display_images.short_description = 'Car Images'

class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'status', 'date', 'is_public')
    list_filter = ('status', 'is_public')
    date_hierarchy = 'date'  # إضافة تصفح حسب التاريخ

class AdAdmin(admin.ModelAdmin):
    list_display = ('name', 'hit', 'start_date', 'end_date', 'location_ad')
    list_filter = ('location_ad',)




class SettingAdminForm(forms.ModelForm):
    home_image_1 = forms.ImageField(required=False, label="Home Image 1")
    home_image_2 = forms.ImageField(required=False, label="Home Image 2")
    home_image_3 = forms.ImageField(required=False, label="Home Image 3")
    
    class Meta:
        model = Setting
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.home_images:
            images = self.instance.get_home_images_list()
            for i in range(1, 4):
                self.fields[f'home_image_{i}'].initial = images[i-1] if len(images) >= i else None
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        import os
        from datetime import datetime
        from django.conf import settings
        from django.core.files.storage import FileSystemStorage
        images = []
        for i in range(1, 4):
            image = self.cleaned_data.get(f'home_image_{i}')
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'site'))
            if image:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{image.name}"
                    
                saved_path = fs.save(filename, image)
                    
                relative_path = f'/media/site/{filename}'
                images.append(relative_path)
        
        if images:
            instance.home_images = ','.join(str(image) for image in images)
        
        if commit:
            instance.save()
        return instance


class SettingAdmin(admin.ModelAdmin):
    form = SettingAdminForm
    list_display = ('site_name', 'email', 'phone')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'logo', 'favicon')
        }),
        ('Social Media', {
            'fields': ('facebook', 'instagram', 'whatsapp')
        }),
        ('Home Page Content', {
            'fields': (
                'home_image_1', 'home_image_2', 'home_image_3',
                'home_words'
            )
        }),
        ('Footer - Company Info', {
            'fields': ('company_description',)
        }),
        ('Footer - Contact Info', {
            'fields': ('address', 'email', 'phone', 'fax')
        }),
    )
    
    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)
    




admin_site.register(Car, CarAdmin)
admin_site.register(Complaint, ComplaintAdmin)
admin_site.register(Ad, AdAdmin)
admin_site.register(Setting, SettingAdmin)