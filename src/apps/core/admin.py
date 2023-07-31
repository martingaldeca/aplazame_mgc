from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, UserTypes
from django.contrib.auth.models import User


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    """
    Creates a custom user admin to see and manage the user information in the django admin
    """
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    list_select_related = ('userprofile',)

    def get_user_type(self, instance):
        return UserTypes.attributes[instance.userprofile.user_type]

    get_user_type.short_description = 'User type'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# Unregister the normal user admin and register our custom user admin
# https://simpleisbetterthancomplex.com/tutorial/2016/11/23/how-to-add-user-profile-to-django-admin.html
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
