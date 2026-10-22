
from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path(
        "logout/confirmation/",
        views.logout_confirmation,
        name="logout_confirmation",
    ),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "student-dashboard/",
        views.student_dashboard,
        name="student_dashboard",
    ),
    path(
        "faculty-dashboard/",
        views.faculty_dashboard,
        name="faculty_dashboard",
    ),

    # Faculty features
    path(
        "announcements/create/",
        views.create_announcement,
        name="create_announcement",
    ),
    path(
        "materials/upload/",
        views.upload_study_material,
        name="upload_material",
    ),
    path(
        "events/create/",
        views.create_event,
        name="create_event",
    ),
    path(
        "faculty/activities/",
        views.faculty_activities,
        name="faculty_activities",
    ),

    # Student features
    path(
        "activities/submit/",
        views.submit_activity,
        name="submit_activity",
    ),
]
