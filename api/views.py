from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Student, Course, Enrollment
from .serializers import (
    StudentSerializer,
    CourseSerializer,
    CourseListSerializer,
    EnrollmentSerializer,
)
from .permissions import IsAdminOrReadOnly


class StudentViewSet(viewsets.ModelViewSet):

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["last_name", "first_name", "date_joined"]
    ordering = ["last_name"]

    @action(detail=True, methods=["get"], url_path="courses")
    def my_courses(self, request, pk=None):
        """GET /api/students/{id}/courses/ — курси конкретного студента."""
        student = self.get_object()
        courses = student.courses.all()
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для курсів.
    Фільтрація за кількістю студентів:
        GET /api/courses/?min_students=5
        GET /api/courses/?max_students=20
    Лише адміністратори можуть створювати/редагувати/видаляти.
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "instructor"]
    ordering_fields = ["title", "created_at", "students_count"]
    ordering = ["title"]

    def get_queryset(self):
        return Course.objects.annotate(students_count=Count("students"))

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        min_s = self.request.query_params.get("min_students")
        max_s = self.request.query_params.get("max_students")

        if min_s is not None:
            try:
                queryset = queryset.filter(students_count__gte=int(min_s))
            except ValueError:
                pass
        if max_s is not None:
            try:
                queryset = queryset.filter(students_count__lte=int(max_s))
            except ValueError:
                pass
        return queryset

    @action(detail=True, methods=["get"], url_path="students")
    def enrolled_students(self, request, pk=None):
        """GET /api/courses/{id}/students/ — список студентів курсу."""
        course = self.get_object()
        from .serializers import StudentBriefSerializer
        serializer = StudentBriefSerializer(course.students.all(), many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    CRUD для зарахувань.
    Фільтрація:
        GET /api/enrollments/?student=1
        GET /api/enrollments/?course=3
    Лише адміністратори можуть змінювати.
    """
    queryset = Enrollment.objects.select_related("student", "course").all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["student", "course"]
    ordering_fields = ["enrolled_at"]
    ordering = ["-enrolled_at"]
