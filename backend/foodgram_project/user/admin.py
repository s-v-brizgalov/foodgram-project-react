from django.contrib import admin

from .models import User, Subscriber


class SubscriberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subscriber',
        'signer'
    )
    search_fields = (
        'subscriber__username',
        'signer__username'
    )


admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(User)
