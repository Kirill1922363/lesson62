from django.contrib import admin
from .models import Student, Course, Enrollment


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "date_joined"]
    search_fields = ["first_name", "last_name", "email"]


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ["student"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "instructor", "student_count", "created_at"]
    search_fields = ["title", "instructor"]
    inlines = [EnrollmentInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "enrolled_at"]
    list_filter = ["course"]
    autocomplete_fields = ["student", "course"]
