# complaints/urls.py
from django.urls import path
from . import views
from .views import mark_complaint_as_solved

urlpatterns = [
    path('complaint_list/', views.complaint_list, name='complaint_list'),
    path('file_complaint/', views.file_complaint, name='file_complaint'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('complaints/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/<int:complaint_id>/solve', views.mark_complaint_as_solved, name='mark_complaint_as_solved'),
    path('admin/mark_complaint_as_unsolved/<int:id>/', views.mark_complaint_as_unsolved, name='mark_complaint_as_unsolved'),
    path('delete/<int:complaint_id>/', views.delete_complaint, name='delete_complaint'),
    path('export_complaints/', views.export_complaints, name='export_complaints'),
    # Add more URL patterns as needed
]
