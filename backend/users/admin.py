from django.contrib import admin

from users.models import Follow


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user',)
    search_fields = ('user',)


admin.site.register(Follow, FollowAdmin)
