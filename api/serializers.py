from rest_framework import serializers
from .models import Student, Course, Enrollment


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Student
        fields = ["id", "first_name", "last_name", "full_name", "email", "date_joined"]
        read_only_fields = ["date_joined"]


class StudentBriefSerializer(serializers.ModelSerializer):
    """Compact serializer used when embedding students inside a Course."""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Student
        fields = ["id", "full_name", "email"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source="student.full_name")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Enrollment
        fields = ["id", "student", "student_name", "course", "course_title", "enrolled_at"]
        read_only_fields = ["enrolled_at"]

    def validate(self, attrs):
        if Enrollment.objects.filter(
            student=attrs["student"], course=attrs["course"]
        ).exists():
            raise serializers.ValidationError(
                "Цей студент вже зарахований на даний курс."
            )
        return attrs


class CourseSerializer(serializers.ModelSerializer):
    """Full serializer that includes enrolled students."""
    enrolled_students = StudentBriefSerializer(source="students", many=True, read_only=True)
    student_count = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = [
            "id", "title", "description", "instructor",
            "created_at", "student_count", "enrolled_students",
        ]
        read_only_fields = ["created_at"]


class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no nested students)."""
    student_count = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ["id", "title", "instructor", "created_at", "student_count"]
        read_only_fields = ["created_at"]
