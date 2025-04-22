from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm, LoginForm, ProfileForm, CarEditForm, CarImageForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from .models import Car, Ad, Setting, Complaint
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string

def get_ads_by_location(location):
    current_time = timezone.now()
    return Ad.objects.filter(
        location_ad__in=location,
        start_date__lte=current_time,
        end_date__gte=current_time
    )

def home(request):
    ads = get_ads_by_location(['home_top','home_bottom','sidebar'])
    # bottom_ads = get_ads_by_location('home_bottom')
    # sidebar_ads = get_ads_by_location('sidebar')
    from itertools import groupby
    from operator import attrgetter
    
    grouped_ads = {
        key: list(group) for key, group in groupby(ads, key=attrgetter('location_ad'))
    }
    
    top_ads = grouped_ads.get('home_top', [])
    bottom_ads = grouped_ads.get('home_bottom', [])
    sidebar_ads = grouped_ads.get('sidebar', [])

    latest_cars = Car.objects.filter(sold=False).order_by('-created_at')[:6]
    latest_cars_sold = Car.objects.filter(sold=True).order_by('-created_at')[:6]
    settings = Setting.objects.first()
    
    from django.contrib.auth.models import User
    
    site_stats = {
        'total_cars': Car.objects.count(),
        'available_cars': Car.objects.filter(sold=False).count(),
        'sold_cars': Car.objects.filter(sold=True).count(),
        'total_users': User.objects.count(),
    }
    
    context = {
        'top_ads': top_ads,
        'bottom_ads': bottom_ads,
        'sidebar_ads': sidebar_ads,
        'latest_cars': latest_cars,
        'latest_cars_sold': latest_cars_sold,
        'settings': settings,
        'site_stats': site_stats, 
    }
    return render(request, 'carDealer/home.html', context)

def car_list(request):
    cars = Car.objects.filter(sold=False).order_by('-created_at')

    brand = request.GET.get('brand')
    model = request.GET.get('model')
    city = request.GET.get('city')
    year = request.GET.get('year')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search')

    if brand:
        cars = cars.filter(brand=brand)
    if model:
        cars = cars.filter(model=model)
    if city:
        cars = cars.filter(city=city)
    if year:
        cars = cars.filter(year=year)
    if min_price:
        cars = cars.filter(price__gte=min_price)
    if max_price:
        cars = cars.filter(price__lte=max_price)
    if search:
        cars = cars.filter(brand__icontains=search) | cars.filter(model__icontains=search)

    paginator = Paginator(cars, 8)  
    page_number = request.GET.get('page')
    cars_page = paginator.get_page(page_number)

    brands = Car.objects.values('brand').distinct()
    models = Car.objects.values('model').distinct()
    cities = Car.objects.values('city').distinct()
    years = Car.objects.values('year').distinct().order_by('-year')
    sidebar_ads = get_ads_by_location(['sidebar'])

    context = {
        'cars': cars_page,
        'brands': [b['brand'] for b in brands],
        'models': [m['model'] for m in models],
        'cities': [c['city'] for c in cities],
        'years': [y['year'] for y in years],
        'sidebar_ads': sidebar_ads,
    }
    return render(request, 'carDealer/car_list.html', context)
    

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    approved_complaints = Complaint.objects.filter(
        car=car,
        status='approved',
        is_public=True
    ).order_by('-date')
    
    if request.user.is_superuser or (request.user.is_authenticated and request.user == car.user):
        approved_complaints = Complaint.objects.filter(
            car=car,
            status='approved'
        ).order_by('-date')
    sidebar_ads = get_ads_by_location('sidebar')
    
    context = {
        'car': car,
        'approved_complaints': approved_complaints,
        'sidebar_ads': sidebar_ads,
    }
    return render(request, 'carDealer/car_detail.html', context)

def track_ad_click(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    ad.hit += 1
    ad.save()
    return HttpResponseRedirect(ad.url)

def submit_complaint(request, car_id):
    if request.method == 'POST':
        car = get_object_or_404(Car, id=car_id)
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        content = request.POST.get('content')
        
        if request.user == car.user:
            messages.error(request, 'You cannot submit a complaint on your own car.')
            return redirect('carDealer:car_detail', car_id=car_id)
        
      
        messages.success(request, 'Your complaint has been submitted successfully!')
        return redirect('carDealer:car_detail', car_id=car_id)
    
    return redirect('carDealer:car_detail', car_id=car_id)

@login_required
def my_cars(request):
    cars = Car.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'carDealer/my_cars.html', {'cars': cars})

@login_required
def add_car(request):
    if request.method == 'POST':
        try:
            
            car = Car(
                user=request.user,
                brand=request.POST['brand'],
                model=request.POST['model'],
                year=request.POST['year'],
                price=request.POST['price'],
                color=request.POST['color'],
                country=request.POST['country'],
                city=request.POST['city'],
                description=request.POST['description'],
                car_images=[] 
            )
            car.save()

            images = request.FILES.getlist('car_images')
            if images:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'cars'))
                image_paths = []
                
                for image in images:
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{image.name}"
                    
                    saved_path = fs.save(filename, image)
                    
                    relative_path = f'/media/cars/{filename}'
                    image_paths.append(relative_path)
                
                car.car_images = image_paths
                car.save()

            messages.success(request, 'Car added successfully!')
            return redirect('carDealer:car_detail', car_id=car.id)
        except Exception as e:
            messages.error(request, f'Error adding car: {str(e)}')
    return render(request, 'carDealer/add_car.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('carDealer:login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'carDealer/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('carDealer:home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'carDealer/login.html', {'form': form})

def about(request):
    settings = Setting.objects.first()
    context = {
        'settings': settings,
    }
    return render(request, 'carDealer/about.html', context)

def contact(request):
    settings = Setting.objects.first()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Send email
        email_subject = f'New Contact Form Submission: {subject}'
        email_message = render_to_string('carDealer/email/contact_form.html', {
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message,
        })
        
        try:
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
                html_message=email_message
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')
        
        return redirect('carDealer:contact')
    
    context = {
        'settings': settings,
    }
    return render(request, 'carDealer/contact.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            profile = request.user.profile
            profile.mobile_number = form.cleaned_data.get('mobile_number')
            profile.city = form.cleaned_data.get('city')
            profile.country = form.cleaned_data.get('country')
            
            if 'profile_photo' in request.FILES:
                profile.profile_photo = request.FILES['profile_photo']
            
            profile.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('carDealer:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=request.user)
    
    cars_count = Car.objects.filter(user=request.user).count()
    
    recent_cars = Car.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'form': form,
        'cars_count': cars_count,
        'recent_cars': recent_cars,
        'profile': request.user.profile,
    }
    return render(request, 'carDealer/profile.html', context)


@login_required
def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id, user=request.user)
    
    if request.method == 'POST':
        form = CarEditForm(request.POST, instance=car)
        if form.is_valid():
            car = form.save()
            messages.success(request, 'Car updated successfully!')
            return redirect('carDealer:car_detail', car_id=car.id)
    else:
        form = CarEditForm(instance=car)
    
    context = {
        'form': form,
        'car': car,
    }
    return render(request, 'carDealer/edit_car.html', context)

@login_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id, user=request.user)
    try:
        car.delete()
        messages.success(request, 'Car deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting car: {str(e)}')
    return redirect('carDealer:my_cars')

@login_required
def delete_car_image(request, car_id, image_index):
    car = get_object_or_404(Car, id=car_id, user=request.user)
    
    try:
        # Remove the image from the car's images list
        if 0 <= image_index < len(car.car_images):
            # Delete the actual file from storage
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'cars'))
            image_path = car.car_images[image_index]
            fs.delete(os.path.basename(image_path))
            
            car.car_images.pop(image_index)
            car.save()
            messages.success(request, 'Image deleted successfully!')
        else:
            messages.error(request, 'Invalid image index')
    except Exception as e:
        messages.error(request, f'Error deleting image: {str(e)}')
    
    return redirect('carDealer:edit_car', car_id=car.id)

@login_required
def sold_car(request, car_id):
    car = get_object_or_404(Car, id=car_id, user=request.user)
    try:
        car.sold = not car.sold
        car.save()
        status = 'sold' if car.sold else 'not sold'
        messages.success(request, f'Car marked as {status}.')
    except Exception as e:
        messages.error(request, f'Error updating car status: {str(e)}')
    return redirect('carDealer:my_cars')