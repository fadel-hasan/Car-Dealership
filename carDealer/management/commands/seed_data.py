from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from carDealer.models import Car, UserProfile
from django.db.models.signals import post_save
from carDealer.models import create_user_profile, save_user_profile

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        post_save.disconnect(create_user_profile, sender=User)
        post_save.disconnect(save_user_profile, sender=User)

        try:
            # 1. إنشاء مستخدمين وملفات تعريف
            users_data = [
                {
                    'username': 'user5',
                    'password': 'password123',
                    'email': 'user5@example.com',
                    'profile': {
                        'mobile_number': '1234567890',
                        'city': 'Riyadh',
                        'country': 'Saudi Arabia',
                        'email_verified': True,
                        # 'profile_photo': 'profiles/user1.jpg'
                    }
                },
                {
                    'username': 'user6',
                    'password': 'password123',
                    'email': 'user6@example.com',
                    'profile': {
                        'mobile_number': '0987654321',
                        'city': 'Jeddah',
                        'country': 'Saudi Arabia',
                        'email_verified': False,
                        # 'profile_photo': 'profiles/user2.jpg'
                    }
                },
            ]

            for user_data in users_data:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={'email': user_data['email']}
                )
                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    UserProfile.objects.get_or_create(
                        user=user,
                        defaults=user_data['profile']
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created user and profile: {user.username}'))

        finally:
            post_save.connect(create_user_profile, sender=User)
            post_save.connect(save_user_profile, sender=User)

        cars_data = [
            {
                'user': User.objects.get(username='user6'),
                'brand': 'Toyota',
                'model': 'Camry',
                'year': 2020,
                'price': 85000.00,
                'car_images': ['/media/cars/camry.jpeg', '/media/cars/camry2.jpeg','/media/cars/camry3.jpeg'],
                'description': 'Well-maintained Toyota Camry in excellent condition.',
                'color': 'White',
                'country': 'Saudi Arabia',
                'city': 'Riyadh',
            },
            {
                'user': User.objects.get(username='user1'),
                'brand': 'Honda',
                'model': 'Civic',
                'year': 2019,
                'price': 75000.00,
                'car_images': ['/media/cars/Civic.jpeg','/media/cars/Civic2.jpeg','/media/cars/Civic3.jpeg'],
                'description': 'Honda Civic with low mileage.',
                'color': 'Black',
                'country': 'Saudi Arabia',
                'city': 'Jeddah',
            },
        ]

        for car_data in cars_data:
            Car.objects.get_or_create(
                user=car_data['user'],
                brand=car_data['brand'],
                model=car_data['model'],
                defaults={
                    'year': car_data['year'],
                    'price': car_data['price'],
                    'car_images': car_data['car_images'],
                    'description': car_data['description'],
                    'color': car_data['color'],
                    'country': car_data['country'],
                    'city': car_data['city'],
                    'sold': False
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Created car: {car_data["brand"]} {car_data["model"]}'))