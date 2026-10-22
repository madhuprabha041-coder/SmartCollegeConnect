
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from .models import (
    Profile,
    Announcement,
    StudyMaterial,
    Event,
    StudentActivity,
)


def get_user_role(user):
    try:
        return user.profile.role
    except Profile.DoesNotExist:
        return None


def home(request):
    return render(request, "core/home.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "")

        if not all([username, email, password, confirm_password, role]):
            messages.error(request, "Please complete all fields.")
        elif role not in ("student", "faculty"):
            messages.error(request, "Please select a valid role.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(
                request, "Password must contain at least 8 characters."
            )
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            Profile.objects.create(user=user, role=role)
            messages.success(
                request, "Registration successful. Please log in."
            )
            return redirect("login")

    return render(request, "core/register.html")


def user_login(request):
    # Already logged-in users can go directly to their dashboard.
    # Logged-out users must enter their username and password.
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(request, "Invalid username or password.")
        elif get_user_role(user) is None:
            messages.error(
                request, "Your account has no assigned role."
            )
        else:
            login(request, user)
            return redirect("dashboard")

    return render(request, "core/login.html")


@login_required
def user_logout(request):
    # Logout must be submitted using POST.
    if request.method != "POST":
        return redirect("dashboard")

    logout(request)
    messages.success(
        request, "You have been logged out successfully."
    )
    return redirect("logout_confirmation")


def logout_confirmation(request):
    # This page can be opened after logout.
    if request.user.is_authenticated:
        return redirect("dashboard")

    return render(request, "core/logout.html")


@login_required
def dashboard(request):
    role = get_user_role(request.user)

    if role == "faculty":
        return redirect("faculty_dashboard")
    elif role == "student":
        return redirect("student_dashboard")

    messages.error(request, "Your account role is not configured.")
    return redirect("home")


@login_required
def faculty_dashboard(request):
    if get_user_role(request.user) != "faculty":
        messages.error(request, "Faculty access only.")
        return redirect("dashboard")

    announcements = Announcement.objects.filter(
        created_by=request.user
    ).order_by("-created_at")

    study_materials = StudyMaterial.objects.filter(
        uploaded_by=request.user
    ).order_by("-uploaded_at")

    events = Event.objects.filter(
        created_by=request.user
    ).order_by("event_date")

    return render(request, "core/faculty_dashboard.html", {
        "announcements": announcements,
        "study_materials": study_materials,
        "events": events,
    })


@login_required
def student_dashboard(request):
    if get_user_role(request.user) != "student":
        messages.error(request, "Student access only.")
        return redirect("dashboard")

    announcements = Announcement.objects.all().order_by("-created_at")
    study_materials = StudyMaterial.objects.all().order_by("-uploaded_at")

    events = Event.objects.filter(
        event_date__gte=timezone.now()
    ).order_by("event_date")

    activities = StudentActivity.objects.filter(
        submitted_by=request.user
    ).order_by("-created_at")

    return render(request, "core/student_dashboard.html", {
        "announcements": announcements,
        "study_materials": study_materials,
        "events": events,
        "activities": activities,
    })


@login_required
def create_announcement(request):
    if get_user_role(request.user) != "faculty":
        messages.error(request, "Faculty access only.")
        return redirect("dashboard")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        message = request.POST.get("message", "").strip()

        if title and message:
            Announcement.objects.create(
                title=title,
                message=message,
                created_by=request.user,
            )
            messages.success(request, "Announcement published.")
            return redirect("faculty_dashboard")

        messages.error(request, "Please fill in all fields.")

    return render(request, "core/create_announcement.html")


@login_required
def upload_study_material(request):
    if get_user_role(request.user) != "faculty":
        messages.error(request, "Faculty access only.")
        return redirect("dashboard")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        uploaded_file = request.FILES.get("file")

        if not title or not uploaded_file:
            messages.error(request, "Title and file are required.")
        elif uploaded_file.size > 10 * 1024 * 1024:
            messages.error(
                request, "File size must not exceed 10 MB."
            )
        else:
            StudyMaterial.objects.create(
                title=title,
                description=description,
                file=uploaded_file,
                uploaded_by=request.user,
            )
            messages.success(request, "Study material uploaded.")
            return redirect("faculty_dashboard")

    return render(request, "core/upload_material.html")


@login_required
def create_event(request):
    if get_user_role(request.user) != "faculty":
        messages.error(request, "Faculty access only.")
        return redirect("dashboard")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        event_date = parse_datetime(
            request.POST.get("event_date", "")
        )
        venue = request.POST.get("venue", "").strip()

        if not all([title, description, event_date, venue]):
            messages.error(
                request, "Please fill in all fields correctly."
            )
        else:
            if timezone.is_naive(event_date):
                event_date = timezone.make_aware(event_date)

            Event.objects.create(
                title=title,
                description=description,
                event_date=event_date,
                venue=venue,
                created_by=request.user,
            )
            messages.success(request, "College event created.")
            return redirect("faculty_dashboard")

    return render(request, "core/create_event.html")


@login_required
def submit_activity(request):
    if get_user_role(request.user) != "student":
        messages.error(request, "Student access only.")
        return redirect("dashboard")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        activity_type = request.POST.get("activity_type", "")
        activity_date = parse_date(
            request.POST.get("activity_date", "")
        )

        valid_types = [
            choice[0] for choice in StudentActivity.ACTIVITY_TYPES
        ]

        if not all([title, description, activity_date]):
            messages.error(
                request, "Please fill in all fields correctly."
            )
        elif activity_type not in valid_types:
            messages.error(
                request, "Please select a valid activity type."
            )
        else:
            StudentActivity.objects.create(
                title=title,
                description=description,
                activity_type=activity_type,
                activity_date=activity_date,
                submitted_by=request.user,
            )
            messages.success(
                request, "Activity submitted successfully."
            )
            return redirect("student_dashboard")

    return render(request, "core/submit_activity.html")


@login_required
def faculty_activities(request):
    if get_user_role(request.user) != "faculty":
        messages.error(request, "Faculty access only.")
        return redirect("dashboard")

    activities = StudentActivity.objects.select_related(
        "submitted_by"
    ).order_by("-created_at")

    return render(request, "core/faculty_activities.html", {
        "activities": activities,
    })
