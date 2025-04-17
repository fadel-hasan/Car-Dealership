from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

app_name = 'carDealer'

urlpatterns = [
    # Main URLs
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('my-cars/', views.my_cars, name='my_cars'),
    path('add-car/', views.add_car, name='add_car'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='carDealer/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='carDealer:home'), name='logout'),
    path('register/', views.register, name='register'),
    path('ad/<int:ad_id>/', views.track_ad_click, name='track_ad_click'),
    path('car/<int:car_id>/submit-complaint/', views.submit_complaint, name='submit_complaint'),
    
    
    path('car/<int:car_id>/edit/', views.edit_car, name='edit_car'),
    path('car/<int:car_id>/sold',views.sold_car,name='mark_as_sold'),
    path('car/<int:car_id>/delete/', views.delete_car, name='delete_car'),
    path('car/<int:car_id>/delete-image/<int:image_index>/', views.delete_car_image, name='delete_car_image'),
]