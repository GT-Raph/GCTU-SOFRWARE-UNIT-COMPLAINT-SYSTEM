from django.contrib.admin import AdminSite

class UserAdminSite(AdminSite):
    site_header = "User Administration"
    site_title = "User Admin Portal"
    index_title = "Welcome to User Admin Portal"

user_admin_site = UserAdminSite(name='user_admin')