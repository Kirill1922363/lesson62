import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edu_platform.settings")
django.setup()

from api.models import Student, Course, Enrollment
from django.contrib.auth import get_user_model

User = get_user_model()

# superuser
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123")
    print("Superuser created: admin / admin123")

# students
students_data = [
    ("Іван", "Петренко", "ivan.petrenko@example.com"),
    ("Олена", "Коваль", "olena.koval@example.com"),
    ("Микола", "Бойко", "mykola.boiko@example.com"),
    ("Тетяна", "Шевченко", "tetiana.shevchenko@example.com"),
    ("Андрій", "Мороз", "andrii.moroz@example.com"),
]
students = []
for fn, ln, email in students_data:
    s, _ = Student.objects.get_or_create(email=email, defaults={"first_name": fn, "last_name": ln})
    students.append(s)
print(f"{len(students)} студентів готово")

# courses
courses_data = [
    ("Python для початківців", "Олексій Ткач"),
    ("Django REST Framework", "Марія Гриценко"),
    ("Алгоритми та структури даних", "Сергій Лисенко"),
]
courses = []
for title, instructor in courses_data:
    c, _ = Course.objects.get_or_create(title=title, defaults={"instructor": instructor, "description": f"Курс: {title}"})
    courses.append(c)
print(f"{len(courses)} курсів готово")

# enrollments
pairs = [(students[0], courses[0]), (students[0], courses[1]),
         (students[1], courses[0]), (students[2], courses[1]),
         (students[3], courses[2]), (students[4], courses[0]),
         (students[4], courses[2])]
for st, co in pairs:
    Enrollment.objects.get_or_create(student=st, course=co)
print(f"{Enrollment.objects.count()} зарахувань готово")
print("Done!")
