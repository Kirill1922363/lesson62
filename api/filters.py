import django_filters
from .models import Course


class CourseFilter(django_filters.FilterSet):

    min_students = django_filters.NumberFilter(method="filter_min_students", label="Мінімум студентів")
    max_students = django_filters.NumberFilter(method="filter_max_students", label="Максимум студентів")

    class Meta:
        model = Course
        fields = ["min_students", "max_students"]

    def filter_min_students(self, queryset, name, value):
        return queryset.filter(students__isnull=False).annotate_count().filter(students_count__gte=value)

    def filter_max_students(self, queryset, name, value):
        return queryset.annotate_count().filter(students_count__lte=value)
