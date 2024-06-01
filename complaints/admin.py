from django.urls import reverse
from django.urls import path
from django.utils.html import format_html
from django.contrib import admin
from django.shortcuts import HttpResponseRedirect
from .models import Complaint, Category, UserProfile, StudentLevel, StudentLevelType
from .forms import ComplaintForm
import requests

admin.site.site_header = 'SOFTWARE UNIT COMPLAINT SYSTEM'


class ComplaintAdmin(admin.ModelAdmin):
    form = ComplaintForm
    list_display = ('student_id', 'category', 'status', 'created_at', 'mark_as_solved_button', 'mark_as_unsolved_button','solved_by', 'solved_at')
    search_fields = ('name', 'student_id', 'phone_number', 'category__name', 'status', 'date_submitted')
    list_filter = ('category', 'status', 'created_at')

    def student_id(self, obj):
        return obj.student_id
    student_id.short_description = 'Student ID'

    def phone_number(self, obj):
        return obj.phone_number
    phone_number.short_description = 'Phone Number'

    def mark_as_solved_button(self, obj):
        if obj.status != 'Solved':
            url = reverse('admin:mark_complaint_as_solved', args=[obj.id])
            return format_html('<a class="button" href="{}">Mark as Solved</a>', url)
        return "-"
    mark_as_solved_button.short_description = 'Mark as Solved'

    def mark_as_unsolved_button(self, obj):
        if obj.status == 'Solved':
            url = reverse('admin:mark_complaint_as_unsolved', args=[obj.id])
            return format_html('<a class="button" href="{}">Mark as Unsolved</a>', url)
        return "-"
    mark_as_unsolved_button.short_description = 'Mark as Unsolved'

    def delete_button(self, obj):
        url = reverse('admin:delete_complaint', args=[obj.id])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_button.short_description = 'Delete'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mark_solved/<int:complaint_id>/', self.mark_solved, name='mark_complaint_as_solved'),
            path('mark_unsolved/<int:complaint_id>/', self.mark_unsolved, name='mark_complaint_as_unsolved'),
            path('delete/<int:complaint_id>/', self.delete_complaint, name='delete_complaint'),
        ]
        return custom_urls + urls

    def mark_solved(self, request, complaint_id):
        # Get the complaint object
        complaint = Complaint.objects.get(pk=complaint_id)
        
        # Check if the complaint is already marked as solved
        if complaint.status == 'Solved':
            self.message_user(request, f'Complaint "{complaint}" is already marked as solved.')
            return HttpResponseRedirect(reverse('admin:complaints_complaint_changelist'))
        
        # Mark the complaint as solved
        complaint.status = 'Solved'
        complaint.save()
        
        # Send SMS to the phone number attached to the complaint
        phone_number = complaint.phone_number
        message = f'Hello {complaint.name}. Your complaint has been marked as solved. Thank you.'
        self.send_sms(phone_number, message)

        self.message_user(request, f'Complaint "{complaint}" marked as solved. SMS sent to {phone_number}.')
        return HttpResponseRedirect(reverse('admin:complaints_complaint_changelist'))

    def mark_unsolved(self, request, complaint_id):
        # Implement the logic to mark the complaint as unsolved
        complaint = Complaint.objects.get(pk=complaint_id)
        complaint.status = 'Pending'  # Assuming 'Pending' is the status for unsolved complaints
        complaint.save()
        self.message_user(request, f'Complaint "{complaint}" marked as unsolved.')
        return HttpResponseRedirect(reverse('admin:complaints_complaint_changelist'))

    def delete_complaint(self, request, complaint_id):
        # Implement the logic to delete the complaint
        complaint = Complaint.objects.get(pk=complaint_id)
        complaint.delete()
        self.message_user(request, f'Complaint "{complaint}" deleted.')
        return HttpResponseRedirect(reverse('admin:complaints_complaint_changelist'))

    def send_sms(self, phone_number, message):
        # Add your SMS sending logic here
        # For example, you can use a third-party API or library to send SMS
        # Replace the following URL and parameters with your actual SMS API endpoint and parameters
        sms_api_url = 'https://erp.gctu.edu.gh/getinformation/send_sms.php'
        payload = {
            'phone_number': phone_number,
            'message': message,
            'api_key': 'your_api_key',
            # Add other necessary parameters
        }
        response = requests.post(sms_api_url, data=payload)
        # Check the response and handle accordingly
        if response.status_code == 200:
            print('SMS sent successfully.')
        else:
            print('Failed to send SMS.')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')  # replace 'name' with your fields
    list_editable = ('is_active',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'display_profile_picture')
    readonly_fields = ('username', 'full_name', 'email')

    def display_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_picture)
        else:
            return "No Image"
    display_profile_picture.short_description = 'Profile Picture'
    


admin.site.register(StudentLevel)
admin.site.register(StudentLevelType)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(Category, CategoryAdmin)
