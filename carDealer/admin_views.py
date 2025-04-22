from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Car, Complaint, Ad
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages

@staff_member_required
def admin_statistics(request):

    context = {
        'total_cars': Car.objects.total_cars(),
        'sold_cars': Car.objects.sold_cars(),
        'active_cars': Car.objects.active_cars(),
        'total_complaints': Complaint.objects.total_complaints(),
        'active_ads': Ad.objects.active_ads(),
        'complaints_by_status': Complaint.objects.comlaints_by_status(),
        'cars_by_brand': Car.objects.cars_by_brand(),
        'recent_sales': Car.objects.recent_sales(),
    }
    
    return render(request, 'admin/statistics.html', context)

@staff_member_required
def manage_complaints(request):
    status = request.GET.get('status')
    is_public = request.GET.get('is_public')
    car_id = request.GET.get('car')

    cars = Car.objects.all()

    complaints = Complaint.objects.all()

    if status:
        complaints = complaints.filter(status=status)
    if is_public is not None:
        complaints = complaints.filter(is_public=is_public)
    if car_id:
        complaints = complaints.filter(car_id=car_id)

    complaints = complaints.order_by('-date')

    paginator = Paginator(complaints, 10)
    page = request.GET.get('page')
    complaints = paginator.get_page(page)

    context = {
        'complaints': complaints,
        'cars': cars,
    }
    return render(request, 'admin/complaints.html', context)

@staff_member_required
def update_complaint(request, complaint_id):
    if request.method == 'POST':
        complaint = Complaint.objects.get(id=complaint_id)
        status = request.POST.get('status')
        
        if status in ['approved', 'rejected']:
            complaint.status = status
            if status == 'approved':
                complaint.is_public = True
            complaint.save()
            messages.success(request, f'Complaint has been {status}.')
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('admin:complaints')


@staff_member_required
def reject_complaint(request, complaint_id):
        if request.method == 'POST':
            try:
                complaint = Complaint.objects.get(id=complaint_id)
                
                complaint.status = 'rejected'
                complaint.is_public = False
                complaint.save()
                
                messages.success(request, f'Complaint has been {complaint.status}.')
            except Complaint.DoesNotExist:
                messages.error(request, 'Invalid status.')
            except Exception as e:
                messages.error(request, f'Error {str(e)}')
        
        return redirect('admin:complaints')
    
    
@staff_member_required
def toggle_public_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == "POST":
        complaint.is_public = int(request.POST.get("is_public"))
        complaint.save()
        messages.success(request, "Public visibility updated successfully.")
    return redirect("admin:complaints")