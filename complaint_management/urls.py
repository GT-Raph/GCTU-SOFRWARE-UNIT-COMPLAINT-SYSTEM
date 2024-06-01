# complaint_management/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from accounts import views
from complaints.views import dashboard, logout_success, mark_complaint_as_solved
from accounts.views import submit_successful_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='login/')),  # Redirect root to login page
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('complaints/', include('complaints.urls')),
    path('submit_successful/', submit_successful_view, name='submit_successful'),
    path('complaints/mark_solved/<int:complaint_id>/', mark_complaint_as_solved, name='mark_complaint_as_solved'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/success/', logout_success, name='logout_success'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Other URL patterns...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)