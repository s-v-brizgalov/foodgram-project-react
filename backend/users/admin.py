from django.conf import settings
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
    )
    empty_value_display = '--пусто--'
    list_filter = ('username', 'email')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_per_page = settings.L_P_P
