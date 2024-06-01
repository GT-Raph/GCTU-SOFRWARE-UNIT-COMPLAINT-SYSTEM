from django.utils.timezone import make_naive
from django.http import HttpResponse
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Complaint, StudentLevel
from .forms import ComplaintForm
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.db import models

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)

# Then, in your view:
def file_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            form.save()
            # get all logged in users
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            user_id_list = []
            for session in sessions:
                data = session.get_decoded()
                user_id_list.append(data.get('_auth_user_id', None))
            logged_in_users = User.objects.filter(id__in=user_id_list)
            # add a notification for each logged in user
            for user in logged_in_users:
                Notification.objects.create(user=user, message='A new complaint has been submitted.')
            return redirect('submit_successful')
    else:
        form = ComplaintForm()
    return render(request, 'complaints/file_complaint.html', {'form': form})

@login_required(login_url='login')
def complaint_list(request):
    complaints = Complaint.objects.all()
    categories = Category.objects.all()
    levels = StudentLevel.objects.all()
    
    filter_day = request.GET.get('day')
    filter_month = request.GET.get('month')
    category = request.GET.get('category')
    filter_status = request.GET.get('status')
    filter_level = request.GET.get('level')  # renamed from 'levels'

    if filter_day:
        complaints = complaints.filter(created_at__day=int(filter_day))
    if filter_month:
        complaints = complaints.filter(created_at__month=int(filter_month))
    if category:
        complaints = complaints.filter(category_id=category)
    if filter_status:
        complaints = complaints.filter(status=filter_status)
    if filter_level:  # new condition
        complaints = complaints.filter(student_level__level=filter_level)

    # ... rest of your view ...

    paginator = Paginator(complaints, 10)  # Show 10 complaints per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'complaints/complaint_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'levels': levels,
    })
    complaints = Complaint.objects.all()
    categories = Category.objects.all()
    levels = StudentLevel.objects.all()
    
    filter_day = request.GET.get('day')
    filter_month = request.GET.get('month')
    category = request.GET.get('category')
    filter_status = request.GET.get('status')
    filter_level = request.GET.get('level')  # renamed from 'levels'

    if filter_day:
        complaints = complaints.filter(created_at__day=int(filter_day))
    if filter_month:
        complaints = complaints.filter(created_at__month=int(filter_month))
    if category:
        complaints = complaints.filter(category_id=category)
    if filter_status:
        complaints = complaints.filter(status=filter_status)
    if filter_level:  # new condition
        complaints = complaints.filter(student_level_id=filter_level)

    paginator = Paginator(complaints, 10)  # Show 10 complaints per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'complaints/complaint_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'levels': levels,
    })


@login_required(login_url='login')
def export_complaints(request):
    complaints = Complaint.objects.all().values()

    # Convert queryset to list to be able to modify it
    complaints_list = list(complaints)

    # Make datetime objects timezone naive
    for complaint in complaints_list:
        if complaint['created_at']:
            complaint['created_at'] = make_naive(complaint['created_at'])

    df = pd.DataFrame(complaints_list)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=complaints.xlsx'
    df.to_excel(response, index=False)

    return response

@login_required(login_url='login')
def dashboard(request):
    total_complaints = Complaint.objects.count()
    solved_complaints = Complaint.objects.filter(status='Solved').count()
    unresolved_complaints = total_complaints - solved_complaints

    today = datetime.now().date()
    complaints_per_day = Complaint.objects.filter(created_at__date=today).count()
    
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    complaints_this_week = Complaint.objects.filter(created_at__range=[week_start, week_end]).count()
    
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    complaints_this_month = Complaint.objects.filter(created_at__range=[month_start, month_end]).count()

    context = {
        'total_complaints': total_complaints,
        'solved_complaints': solved_complaints,
        'unresolved_complaints': unresolved_complaints,
        'complaints_per_day': complaints_per_day,
        'complaints_this_week': complaints_this_week,
        'complaints_this_month': complaints_this_month,
    }

    return render(request, 'complaints/dashboard.html', context)

@login_required(login_url='login')
def mark_complaint_as_solved(request, complaint_id):
    # Get the complaint object
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    complaint.solved_by = request.user
    complaint.solved_at = timezone.now()
    # Check if the complaint is already marked as solved
    if complaint.status == 'Solved':
        messages.error(request, f'Complaint "{complaint}" is already marked as solved.')
    else:
        # Mark the complaint as solved
        complaint.status = 'Solved'
        complaint.save()
        messages.success(request, f'Complaint "{complaint}" marked as solved.')

    return redirect(reverse('complaint_list'))



def mark_complaint_as_unsolved(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    complaint.status = 'Unsolved'
    complaint.save()
    return redirect('admin:complaint_list')


@login_required(login_url='login')
def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.delete()
    return redirect('complaint_list')

def logout_success(request):
    return render(request, 'complaints/logout_success.html')

def update_admin_status(complaint, is_checked):
    content_type = ContentType.objects.get_for_model(complaint)
    log_entry = LogEntry.objects.filter(content_type=content_type, object_id=complaint.id).first()

    if log_entry:
        log_entry.action_flag = CHANGE if is_checked == '1' else 0
        log_entry.save()


def submit_successful_view(request):
    return render(request, 'submit_successful.html')


def serialize_complaint(complaint):
    return {
        'id': complaint.id,
        'name': complaint.name,
        'student_id': complaint.student_id,
        'phone_number': complaint.phone_number,
        'student_level': complaint.student_level,
        'student_level_type': complaint.student_level_type,
        'category': complaint.category.name,
        'description': complaint.description,
        'status': complaint.status,
        'created_at': complaint.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }

def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    serialized_data = serialize_complaint(complaint)
    return JsonResponse(serialized_data)

def complaint_form_submit(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save()
            # get all logged in users
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            user_id_list = []
            for session in sessions:
                data = session.get_decoded()
                user_id_list.append(data.get('_auth_user_id', None))
            logged_in_users = User.objects.filter(id__in=user_id_list)
            # add a message for each logged in user
            for user in logged_in_users:
                messages.success(user, 'A new complaint has been submitted.')
            return redirect('complaint_detail', complaint_id=complaint.id)
    else:
        form = ComplaintForm()
    return render(request, 'complaint_form.html', {'form': form})