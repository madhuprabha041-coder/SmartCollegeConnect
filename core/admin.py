
from django.contrib import admin
from .models import (
    Profile,
    Announcement,
    StudyMaterial,
    Event,
    StudentActivity,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at")
    search_fields = ("title", "message")


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_by", "uploaded_at")
    search_fields = ("title",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "venue", "created_by")


@admin.register(StudentActivity)
class StudentActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title", "activity_type", "activity_date", "submitted_by"
    )
    list_filter = ("activity_type",)
    search_fields = ("title", "description")
