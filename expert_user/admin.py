from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from expert_user.models import ExUser


class ExInline(admin.StackedInline):
    model = ExUser
    can_delete = False
    verbose_name_plural = "ExUser"


class ExUserAdmin(UserAdmin):
    inlines = (ExInline,)


admin.site.unregister(User)
admin.site.register(User, ExUserAdmin)
