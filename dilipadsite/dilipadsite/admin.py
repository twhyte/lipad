from django.contrib import admin
from dilipadsite.models import party
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from dilipadsite.models import Blogger

admin.site.register(party)

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class BloggerInline(admin.StackedInline):
    model = Blogger
    can_delete = False
    verbose_name_plural = 'blogger'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (BloggerInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
