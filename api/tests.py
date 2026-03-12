from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Student, Course, Enrollment

User = get_user_model()


class StudentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser("admin", "a@a.com", "pass")
        self.student_user = User.objects.create_user("user", "u@u.com", "pass")
        self.s1 = Student.objects.create(first_name="Іван", last_name="Петренко", email="ivan@test.com")
        self.s2 = Student.objects.create(first_name="Олена", last_name="Коваль", email="olena@test.com")

    def test_list_unauthenticated(self):
        r = self.client.get("/api/students/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_search_by_name(self):
        r = self.client.get("/api/students/?search=Іван")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(r.data["results"][0]["first_name"], "Іван")

    def test_search_by_email(self):
        r = self.client.get("/api/students/?search=olena@test.com")
        self.assertEqual(r.data["count"], 1)

    def test_create_requires_admin(self):
        self.client.force_authenticate(user=self.student_user)
        r = self.client.post("/api/students/", {"first_name": "X", "last_name": "Y", "email": "xy@x.com"})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post("/api/students/", {"first_name": "Нова", "last_name": "Особа", "email": "nova@test.com"})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)


class CourseAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser("admin2", "aa@a.com", "pass")
        self.c1 = Course.objects.create(title="Python", instructor="Тест")
        self.c2 = Course.objects.create(title="Django", instructor="Тест2")
        self.st1 = Student.objects.create(first_name="A", last_name="B", email="a@b.com")
        self.st2 = Student.objects.create(first_name="C", last_name="D", email="c@d.com")
        Enrollment.objects.create(student=self.st1, course=self.c1)
        Enrollment.objects.create(student=self.st2, course=self.c1)

    def test_filter_min_students(self):
        r = self.client.get("/api/courses/?min_students=2")
        self.assertEqual(r.status_code, 200)
        titles = [x["title"] for x in r.data["results"]]
        self.assertIn("Python", titles)
        self.assertNotIn("Django", titles)

    def test_filter_max_students(self):
        r = self.client.get("/api/courses/?max_students=0")
        titles = [x["title"] for x in r.data["results"]]
        self.assertIn("Django", titles)
        self.assertNotIn("Python", titles)

    def test_detail_shows_enrolled_students(self):
        r = self.client.get(f"/api/courses/{self.c1.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data["enrolled_students"]), 2)

    def test_enrolled_students_action(self):
        r = self.client.get(f"/api/courses/{self.c1.id}/students/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)


class EnrollmentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser("admin3", "aaa@a.com", "pass")
        self.st = Student.objects.create(first_name="X", last_name="Y", email="xy@test.com")
        self.co = Course.objects.create(title="Test Course", instructor="I")

    def test_create_enrollment(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post("/api/enrollments/", {"student": self.st.id, "course": self.co.id})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_duplicate_enrollment_rejected(self):
        Enrollment.objects.create(student=self.st, course=self.co)
        self.client.force_authenticate(user=self.admin)
        r = self.client.post("/api/enrollments/", {"student": self.st.id, "course": self.co.id})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
