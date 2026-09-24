from django.db import models

import random
import string
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    GENDER_CHOICES =(
        ("male",'Male'),
        ('female','Female'),
        ('other','Other'),
    )
    
    ROLE_CHOICES =(
        ('admin','Admin'),
        ('teacher','Teacher'),
        ('student','Student'),
    )
    
    session = models.ForeignKey(
    "Session",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="students"
)
    
    roll = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    face_image = models.ImageField(
    upload_to="student_faces/",
    blank=True,
    null=True
)
    position = models.ForeignKey(
        "Position",
        on_delete=models.SET_NULL,
        null = True,
        blank=True,
        related_name="teachers"
        
    )
    
    email = models.EmailField(
        unique=True
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(
        blank=True,
        null = True
    )
    address = models.TextField(
        blank=True,
        null = True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )
    profile_image = models.ImageField(
        upload_to="student_profiles/",
        blank=True,
        null=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=["username"]
    
    def __str__(self):
        return self.email
    
    
    
class Session(models.Model):
    year = models.CharField(
        max_length=20
    )
    is_graduated= models.BooleanField(
        default = False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return f"{self.year}"
    
class Position(models.Model):
    name=models.CharField(
        max_length=100,
        unique=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return self.name
    
    
class Course(models.Model):
    
    YEAR_CHOICES = (
        ("1st", "1st Year"),
        ("2nd", "2nd Year"),
        ("3rd", "3rd Year"),
        ("4th", "4th Year"),
    )

    SEMESTER_CHOICES = (
        ("1st", "1st Semester"),
        ("2nd", "2nd Semester"),
    )

    course_code = models.CharField(
        max_length=20
    )

    course_name = models.CharField(
        max_length=200
    )

    year = models.CharField(
        max_length=10,
        choices=YEAR_CHOICES,
        null=True,
        blank=True,
    )

    semester = models.CharField(
        max_length=10,
        choices=SEMESTER_CHOICES,
        null=True,
        blank=True,
    )

    credit = models.DecimalField(
        max_digits=3,
        decimal_places=1
    )

    session = models.ForeignKey(
        "Session",
        on_delete=models.CASCADE,
        related_name="courses"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_courses"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "course_code"],
                name="unique_course_code_per_session"
            )
        ]

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
    
class ClassTestMark(models.Model):
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="class_test_marks"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="class_test_marks"
    )

    ct1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    ct2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    ct3 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    semester_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "student"],
                name="unique_student_course_ct"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.course}"
    
    
class SemesterQuestionPattern(models.Model):
    
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name="semester_question_pattern"
    )

    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=50
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.course.course_code} - "
            f"Semester Pattern"
        )

    def get_total_set_marks(self):
        return sum(
            question_set.total_marks
            for question_set in self.question_sets.all()
        )
        
        
class SemesterQuestionSet(models.Model):
    
    pattern = models.ForeignKey(
        SemesterQuestionPattern,
        on_delete=models.CASCADE,
        related_name="question_sets"
    )

    set_name = models.CharField(
        max_length=20
    )

    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    order = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["pattern", "set_name"],
                name="unique_set_name_per_pattern"
            )
        ]

    def __str__(self):
        return (
            f"{self.pattern.course.course_code} - "
            f"Set {self.set_name}"
        )

    def get_total_subquestion_marks(self):
        return sum(
            question.marks
            for question in self.subquestions.all()
        )
        
class SemesterSubQuestion(models.Model):
    
    question_set = models.ForeignKey(
    SemesterQuestionSet,
    on_delete=models.CASCADE,
    related_name="subquestions"
)

    question_label = models.CharField(
        max_length=20
    )

    marks = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    order = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["question_set", "question_label"],
                name="unique_subquestion_per_set"
            )
        ]

    def __str__(self):
        return (
            f"Set {self.question_set.set_name} - "
            f"{self.question_label}"
        )
        
class SemesterSubQuestionMark(models.Model):
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="semester_subquestion_marks"
    )

    sub_question = models.ForeignKey(
    SemesterSubQuestion,
    on_delete=models.CASCADE,
    related_name="student_marks",
    null=True,
    blank=True
)

    obtained_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "sub_question"],
                name="unique_student_subquestion_mark"
            )
        ]

    def __str__(self):
        return (
            f"{self.student.email} - "
            f"{self.sub_question.question_label} - "
            f"{self.obtained_marks}"
        )

    def save(self, *args, **kwargs):

        if self.obtained_marks < 0:
            self.obtained_marks = 0

        if self.obtained_marks > self.sub_question.marks:
            raise ValueError(
                "Obtained marks cannot be greater than question marks."
            )

        super().save(*args, **kwargs)

        course = (
            self.sub_question
            .question_set
            .pattern
            .course
        )

        total_semester_marks = sum(
            mark.obtained_marks
            for mark in SemesterSubQuestionMark.objects.filter(
                student=self.student,
                sub_question__question_set__pattern__course=course
            )
        )

        ClassTestMark.objects.update_or_create(
            course=course,
            student=self.student,
            defaults={
                "semester_marks": total_semester_marks
            }
        )
    
    
class AttendanceSession(models.Model):
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="attendance_sessions"
    )

    class_number = models.PositiveIntegerField(default=1)

    date = models.DateField(  null=True,
    blank=True)

    code = models.CharField(
        max_length=6,
        unique=True
    )
    
    is_held = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    classroom_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    classroom_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    allowed_radius = models.PositiveIntegerField(
        default=50
    )

    network_identifier = models.CharField(
        max_length=64,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "class_number"],
                name="unique_course_class_number"
            )
        ]

    def __str__(self):
        return (
            f"{self.course.course_code} - "
            f"Class {self.class_number} - "
            f"{self.date}"
        )

def generate_attendance_code():

    while True:

        code = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        if not AttendanceSession.objects.filter(
            code=code
        ).exists():
            return code
        
class AttendanceRecord(models.Model):
    
    attendance_session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="records"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        null=True,
        blank=True
    )

    METHOD_CHOICES = [
        ("face", "Face Verification"),
        ("manual", "Manual"),
    ]

    method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        null=True,
        blank=True
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attendance_session", "student"],
                name="unique_attendance_per_student"
            )
        ]

    def __str__(self):
        return (
            f"{self.student.username} - "
            f"{self.attendance_session.course.course_code}"
        )
        
        
class Notice(models.Model):
    
    title = models.CharField(max_length=200)

    message = models.TextField(blank=True, null=True)

    pdf_file = models.FileField(
        upload_to="notices/pdfs/",
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to="notices/images/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        
        

class Notification(models.Model):
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=50,
        default="general"
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.title}"
    
    
class BusNotice(models.Model):
    
    title = models.CharField(max_length=200)

    message = models.TextField()

    pdf_file = models.FileField(
        upload_to="bus_notices/pdf/",
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to="bus_notices/images/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title