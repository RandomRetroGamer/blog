from django.contrib import admin
from .models import Comment, Group, Post, Event
"""
this is to set up register the models we create
"""

admin.site.register(Post)
admin.site.register(Comment)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "starts_at", "ends_at", "is_closed"]
    list_filter = ["is_closed", "starts_at"]
    search_fields = ["title", "description"]
    filter_horizontal = ["members"]

# lets admins create groups and see who joined them
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ["name"]}
    filter_horizontal = ["members"]