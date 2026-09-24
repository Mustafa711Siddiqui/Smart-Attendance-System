from decimal import Decimal, InvalidOperation
import ipaddress

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from.models import User,Session,Position,Course,ClassTestMark,AttendanceSession,generate_attendance_code,AttendanceRecord, Notice,Notification,BusNotice
from datetime import timedelta
from django.utils import timezone
import base64
import numpy as np
import cv2
import face_recognition

from django.http import JsonResponse
from django.utils import timezone
from .models import (
    SemesterQuestionPattern,
    SemesterQuestionSet,
    SemesterSubQuestion,
    SemesterSubQuestionMark,
)
from.forms import(
    LoginForm,
    TeacherCreateForm,
    RegisterForm,
    StudentProfileForm,
    SessionForm,
    CourseForm,
    SemesterQuestionPatternForm,
    SemesterQuestionSetForm,
    SemesterSubQuestionForm,
    SemesterSubQuestionMarkForm,
    
)


def get_request_network_identifier(request):

    client_address = request.META.get("REMOTE_ADDR")

    if not client_address:
        return None

    try:
        address = ipaddress.ip_address(client_address)
    except ValueError:
        return None

    prefix_length = 24 if address.version == 4 else 64

    return str(
        ipaddress.ip_network(
            f"{address}/{prefix_length}",
            strict=False
        )
    )

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method =="POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            
            login(request,user)
            return redirect("home")
        
    else :
        form = LoginForm()
    return render(request,"accounts/login.html",{
        "form":form
    })
    
    
def Logout_view(request):
    logout(request)
    return redirect("home")






def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        
    else:
        form = RegisterForm()
        
    return render(request,"accounts/register.html",{
        "form":form
    })
    
    
def index(reqeust):
    return render(reqeust,"index.html")

def home(request):
    return render(request,"home.html")


@login_required
def student_dashboard(request):
    if request.user.role!="student":
        return redirect("dashboard")
    if request.method =="POST":
        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            form.save()
            return redirect("student_dashboard")
        
    else :
        form = StudentProfileForm(
            instance=request.user
        )
    return render(
        request,
        "student/dashboard.html",
        {
            "form":form,
            "student":request.user,
        }
    )
    
@login_required
def admin_dashboard(request):
    return render(request,"admin/dashboard.html")


@login_required
def teacher_dashboard(request):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    courses = Course.objects.filter(
        teacher=teacher
    ).select_related(
        "session"
    ).order_by("id")

    sessions = Session.objects.filter(
        courses__teacher=teacher
    ).distinct().order_by("-year")

    return render(
        request,
        "teacher/dashboard.html",
        {
            "teacher": teacher,
            "courses": courses,
            "sessions": sessions,
        }
    )
    
    
@login_required
def teacher_session_courses(request, session_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user


    courses = Course.objects.filter(
        teacher=teacher,
        session_id=session_id
    )

    if not courses.exists():
        return redirect("teacher_dashboard")

    # Unique Years
    years = courses.values_list(
        "year",
        flat=True
    ).distinct()

    session = Session.objects.get(
        id=session_id
    )

    return render(
        request,
        "teacher/session_courses.html",
        {
            "teacher": teacher,
            "session": session,
            "years": years,
        }
    )
    
@login_required

def teacher_year_courses(request,session_id,year):
    if request.user.role != "teacher":
        return redirect("dashboard")
    
    teacher = request.user
    courses = Course.objects.filter(
        teacher = teacher,
        session_id = session_id,
        year=year
    )
    if not courses.exists():
        return redirect("teacher_dashboard")
    
    session = Session.objects.get(
        id=session_id
    )
    
    semesters = courses.values_list(
        "semester",
        flat=True
    ).distinct()
    
    return render(
        request,
        "teacher/year_courses.html",
        {
            "teacher": teacher,
            "session": session,
            "year":year,
            "semesters": semesters
        }
    )
    
@login_required
def teacher_semester_courses(request, session_id, year, semester):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    courses = Course.objects.filter(
        teacher=teacher,
        session_id=session_id,
        year=year,
        semester=semester
    ).select_related(
        "session"
    ).order_by("course_code")

    if not courses.exists():
        return redirect(
            "teacher_year_courses",
            session_id=session_id,
            year=year
        )

    session = Session.objects.get(
        id=session_id
    )

    return render(
        request,
        "teacher/semester_courses.html",
        {
            "teacher": teacher,
            "session": session,
            "year": year,
            "semester": semester,
            "courses": courses,
        }
    )
    
@login_required
def teacher_course_detail(request, course_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    # Get the course
    course = Course.objects.filter(
        id=course_id,
        teacher=teacher
    ).select_related(
        "session"
    ).first()

    # Course not found
    if course is None:
        return redirect("teacher_dashboard")

    # Get all students from this course's session
    students = User.objects.filter(
        role="student",
        session=course.session
    ).order_by(
        "first_name",
        "last_name"
    )

    return render(
        request,
        "teacher/course_detail.html",
        {
            "teacher": teacher,
            "course": course,
            "students": students,
        }
    )
    
    
    
@login_required
def dashboard(request):
    if request.user.role =="admin":
        return redirect("admin_dashboard")
    elif request.user.role =="teacher":
        return redirect("teacher_dashboard")
    
    elif request.user.role == "student":
        return redirect("student_dashboard")
    
    return redirect("login")


@login_required
def student_managemnet(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    students = User.objects.filter(
        role="student"
    ).select_related(
        "session",
        "position"
    )

    sessions = Session.objects.all().order_by("-year")

    session_id = request.GET.get("session")

    # Session filter
    if session_id:
        students = students.filter(
            session_id=session_id
        )

    # Filter করার পর Roll অনুযায়ী increasing order
    students = students.order_by("roll")

    return render(
        request,
        "admin/student_management.html",
        {
            "students": students,
            "sessions": sessions,
        }
    )
    
    
@login_required
def admin_student_profile(request, student_id):

    if request.user.role != "admin":
        return redirect("dashboard")

    student = User.objects.filter(
        id=student_id,
        role="student"
    ).select_related(
        "session",
        "position"
    ).first()

    if not student:
        return redirect("student_managemnet")

    return render(
        request,
        "admin/student_profile.html",
        {
            "student": student,
        }
    )
    
    
@login_required
def student_courses(request):

    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    courses = Course.objects.filter(
        session=student.session
    )

    years = courses.values_list(
        "year",
        flat=True
    ).distinct()

    return render(
        request,
        "student/courses.html",
        {
            "student": student,
            "years": years,
        }
    )
    
@login_required
def student_year_courses(request, session_id, year):

    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    # Student must belong to this session
    if student.session_id != session_id:
        return redirect("student_courses")

    # Get courses for this session and year
    courses = Course.objects.filter(
        session_id=session_id,
        year=year
    )

    if not courses.exists():
        return redirect("student_courses")

    # Get unique semesters
    semesters = courses.values_list(
        "semester",
        flat=True
    ).distinct()

    return render(
        request,
        "student/year_courses.html",
        {
            "student": student,
            "session": student.session,
            "year": year,
            "semesters": semesters,
        }
    )
    
@login_required
def student_semester_courses(request, session_id, year, semester):

    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    # Student must belong to this session
    if student.session_id != session_id:
        return redirect("student_courses")

    # Get courses for this session + year + semester
    courses = Course.objects.filter(
        session_id=session_id,
        year=year,
        semester=semester
    ).select_related(
        "teacher"
    ).order_by(
        "course_code"
    )

    if not courses.exists():
        return redirect(
            "student_year_courses",
            session_id=session_id,
            year=year
        )

    return render(
        request,
        "student/semester_courses.html",
        {
            "student": student,
            "session": student.session,
            "year": year,
            "semester": semester,
            "courses": courses,
        }
    )



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Course, ClassTestMark, Notification
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def teacher_class_test_marks(request, course_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    course = Course.objects.filter(
        id=course_id,
        teacher=teacher
    ).select_related("session").first()

    if not course:
        return redirect("teacher_dashboard")

    students = User.objects.filter(
        role="student",
        session=course.session
    ).order_by("roll")

    if request.method == "POST":

        notifications = []
        has_error = False

        for student in students:

            ct1 = request.POST.get(
                f"ct1_{student.id}"
            )

            ct2 = request.POST.get(
                f"ct2_{student.id}"
            )

            ct3 = request.POST.get(
                f"ct3_{student.id}"
            )

            semester_marks = request.POST.get(
                f"semester_marks_{student.id}"
            )

            mark, created = ClassTestMark.objects.get_or_create(
                course=course,
                student=student
            )

            old_ct1 = (
                str(mark.ct1)
                if mark.ct1 is not None
                else ""
            )

            old_ct2 = (
                str(mark.ct2)
                if mark.ct2 is not None
                else ""
            )

            old_ct3 = (
                str(mark.ct3)
                if mark.ct3 is not None
                else ""
            )

            old_semester_marks = (
                str(mark.semester_marks)
                if mark.semester_marks is not None
                else ""
            )

            new_ct1 = ct1.strip() if ct1 else ""
            new_ct2 = ct2.strip() if ct2 else ""
            new_ct3 = ct3.strip() if ct3 else ""

            new_semester_marks = (
                semester_marks.strip()
                if semester_marks
                else ""
            )

            # Semester marks validation
            if new_semester_marks:

                try:
                    semester_value = Decimal(
                        new_semester_marks
                    )

                    if (
                        semester_value < 0
                        or semester_value > 70
                    ):
                        messages.error(
                            request,
                            f"{student.get_full_name()} এর "
                            f"Semester Marks 0 থেকে 70 এর মধ্যে হতে হবে।"
                        )

                        has_error = True
                        continue

                except InvalidOperation:

                    messages.error(
                        request,
                        f"{student.get_full_name()} এর "
                        f"Semester Marks সঠিক সংখ্যা নয়।"
                    )

                    has_error = True
                    continue

            # Save marks
            mark.ct1 = (
                Decimal(new_ct1)
                if new_ct1
                else None
            )

            mark.ct2 = (
                Decimal(new_ct2)
                if new_ct2
                else None
            )

            mark.ct3 = (
                Decimal(new_ct3)
                if new_ct3
                else None
            )

            mark.semester_marks = (
                Decimal(new_semester_marks)
                if new_semester_marks
                else None
            )

            mark.save()

            marks_changed = (
                old_ct1 != new_ct1
                or old_ct2 != new_ct2
                or old_ct3 != new_ct3
                or old_semester_marks != new_semester_marks
            )

            if marks_changed:

                notifications.append(
                    Notification(
                        recipient=student,
                        title="Marks Updated",
                        message=(
                            f"Your marks for "
                            f"{course.course_code} - "
                            f"{course.course_name} "
                            f"have been updated."
                        ),
                        notification_type="marks_updated",
                    )
                )

        if notifications:

            Notification.objects.bulk_create(
                notifications
            )

        if not has_error:

            messages.success(
                request,
                "All marks have been updated successfully."
            )

        return redirect(
            "teacher_class_test_marks",
            course_id=course.id
        )

    # Existing marks load
    marks = ClassTestMark.objects.filter(
        course=course
    )

    marks_dict = {
        mark.student_id: mark
        for mark in marks
    }

    # Saved marks student-এর সাথে attach করা
    for student in students:
        student.saved_marks = marks_dict.get(
            student.id
        )

    return render(
        request,
        "teacher/class_test_marks.html",
        {
            "course": course,
            "students": students,
        }
    )
    

@login_required
def teacher_start_attendance(request, attendance_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    attendance = AttendanceSession.objects.filter(
        id=attendance_id,
        course__teacher=teacher
    ).select_related(
        "course",
        "course__session"
    ).first()

    if not attendance:
        return redirect("teacher_dashboard")

    if not attendance.is_held or not attendance.date:
        return redirect(
            "teacher_attendance_register",
            course_id=attendance.course.id
        )

    # Starting an inactive session requires a server-visible network.
    if not attendance.is_active:

        if request.method != "POST":
            return redirect(
                "teacher_attendance_register",
                course_id=attendance.course.id
            )

        network_identifier = get_request_network_identifier(request)

        if not network_identifier:
            return JsonResponse({
                "success": False,
                "message": "Unable to determine the teacher network."
            }, status=400)

        now = timezone.now()

        attendance.code = generate_attendance_code()
        attendance.network_identifier = network_identifier

        attendance.expires_at = (
            now + timedelta(minutes=10)
        )

        attendance.is_active = True

        attendance.save(
            update_fields=[
                "code",
                "expires_at",
                "is_active",
                "network_identifier"
            ]
        )

        return JsonResponse({
            "success": True,
            "message": "Attendance started successfully."
        })

    return render(
        request,
        "teacher/attendance_session.html",
        {
            "teacher": teacher,
            "course": attendance.course,
            "attendance": attendance,
        }
    )
    
    
@login_required
def teacher_set_attendance_timer(request, attendance_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    attendance = AttendanceSession.objects.filter(
        id=attendance_id,
        course__teacher=request.user
    ).select_related(
        "course",
        "course__session"
    ).first()

    if not attendance:
        return redirect("teacher_dashboard")

    if not attendance.is_active:
        return redirect(
            "teacher_attendance_register",
            course_id=attendance.course.id
        )

    if request.method == "POST":

        minutes = request.POST.get("minutes")

        try:
            minutes = int(minutes)

        except (TypeError, ValueError):
            minutes = 10

        # Allowed timer values
        if minutes not in [5, 10, 15, 20, 30, 45, 60]:
            minutes = 10

        attendance.expires_at = (
            timezone.now() + timedelta(minutes=minutes)
        )

        attendance.save(
            update_fields=[
                "expires_at"
            ]
        )

    return redirect(
        "teacher_start_attendance",
        attendance_id=attendance.id
    )
    
@login_required
def teacher_end_attendance(request, attendance_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    attendance = AttendanceSession.objects.filter(
        id=attendance_id,
        course__teacher=teacher
    ).select_related("course").first()

    if not attendance:
        return redirect("teacher_dashboard")

    if request.method == "POST":

        attendance.is_active = False

        attendance.save(
            update_fields=["is_active"]
        )

        return redirect(
            "teacher_attendance_register",
            course_id=attendance.course.id
        )

    return redirect(
        "teacher_attendance_register",
        course_id=attendance.course.id
    )
    
    
@login_required
def teacher_create_attendance_classes(request, course_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    course = Course.objects.filter(
        id=course_id,
        teacher=teacher
    ).first()

    if not course:
        return redirect("teacher_dashboard")

    # Already created classes
    existing_classes = AttendanceSession.objects.filter(
        course=course
    ).count()

    # Create remaining classes up to 39
    if request.method == "POST":

        for class_number in range(existing_classes + 1, 40):

            AttendanceSession.objects.create(
                course=course,
                class_number=class_number,
                date=timezone.now().date(),
                code=generate_attendance_code(),
                expires_at=timezone.now() + timedelta(minutes=10),
                is_active=False
            )

        return redirect(
            "teacher_attendance_register",
            course_id=course.id
        )

    return render(
        request,
        "teacher/create_attendance_classes.html",
        {
            "teacher": teacher,
            "course": course,
            "existing_classes": existing_classes,
        }
    )
    
    
@login_required
def teacher_attendance_register(request, course_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    course = Course.objects.filter(
        id=course_id,
        teacher=teacher
    ).select_related("session").first()

    if not course:
        return redirect("teacher_dashboard")

    attendance_sessions = AttendanceSession.objects.filter(
        course=course
    ).order_by("class_number")

    students = User.objects.filter(
    role="student",
    session=course.session
).order_by("roll")

    # ==============================
    # MANUAL ATTENDANCE
    # ==============================

    if request.method == "POST":

        attendance_id = request.POST.get("attendance_id")
        student_id = request.POST.get("student_id")
        status = request.POST.get("status")

        attendance = attendance_sessions.filter(
            id=attendance_id
        ).first()

        student = students.filter(
            id=student_id
        ).first()

        if attendance and student and status in ["present", "absent"]:

            AttendanceRecord.objects.update_or_create(
                attendance_session=attendance,
                student=student,
                defaults={
                    "status": status,
                    "method": "manual",
                    "verified_at": timezone.now(),
                }
            )

        return redirect(
            "teacher_attendance_register",
            course_id=course.id
        )

    # ==============================
    # ATTENDANCE RECORDS
    # ==============================

    records = AttendanceRecord.objects.filter(
        attendance_session__course=course
    )

    records_map = {
        (record.attendance_session_id, record.student_id): record
        for record in records
    }

    # ==============================
    # BUILD REGISTER
    # ==============================

    register = []

    held_sessions = attendance_sessions.filter(is_held=True)

    total_classes = held_sessions.count()

    for student in students:

        cells = []

        present_count = 0
        absent_count = 0

        for attendance in attendance_sessions:

            record = records_map.get(
                (attendance.id, student.id)
            )

            status = record.status if record else None

            # শুধু অনুষ্ঠিত class count হবে
            if attendance.is_held:

                if status == "present":
                    present_count += 1

                elif status == "absent":
                    absent_count += 1

            cells.append({
                "attendance": attendance,
                "record": record,
                "status": status,
            })

        if total_classes > 0:
            percentage = (
                present_count / total_classes
            ) * 100
        else:
            percentage = 0

        register.append({
            "student": student,
            "cells": cells,
            "present": present_count,
            "absent": absent_count,
            "percentage": round(percentage, 2),
        })
    return render(
        request,
        "teacher/attendance_register.html",
        {
            "teacher": teacher,
            "course": course,
            "attendance_sessions": attendance_sessions,
            "register": register,
            "total_classes": total_classes,
        }
    )  
    
    
@login_required
def teacher_set_attendance_date(request, attendance_id):

    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    attendance = AttendanceSession.objects.filter(
        id=attendance_id,
        course__teacher=teacher
    ).select_related("course").first()

    if not attendance:
        return redirect("teacher_dashboard")

    if request.method == "POST":

        date = request.POST.get("date")

        # =========================
        # DATE CLEAR
        # =========================
        if not date:

            # এই class-এর সব attendance delete
            AttendanceRecord.objects.filter(
                attendance_session=attendance
            ).delete()

            # class আবার Not Held
            attendance.date = None
            attendance.is_held = False
            attendance.is_active = False

            attendance.save(
                update_fields=[
                    "date",
                    "is_held",
                    "is_active",
                ]
            )

        # =========================
        # DATE SET
        # =========================
        else:

            attendance.date = date
            attendance.is_held = True

            attendance.save(
                update_fields=[
                    "date",
                    "is_held",
                ]
            )

        return redirect(
            "teacher_attendance_register",
            course_id=attendance.course.id
        )

    return redirect(
        "teacher_attendance_register",
        course_id=attendance.course.id
    )
    

@login_required
def student_class_test_marks(request):
    
    if request.user.role !="student":
        return redirect("dashboard")
    
    student = request.user
    
    courses = Course.objects.filter(
        session = student.session
    )
    
    years = courses.values_list(
        "year",
        flat = True
    ).distinct().order_by("year")
    
    return render(
        request,
        "student/class_test_marks.html",
        {
            "student":student,
            "years": years,
        }
    )
    
    
    
@login_required
def student_marks_year(request, session_id, year):

    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    # Student can only access his/her own session
    if student.session_id != session_id:
        return redirect("student_class_test_marks")

    # Courses for selected year
    courses = Course.objects.filter(
        session_id=session_id,
        year=year
    )

    if not courses.exists():
        return redirect("student_class_test_marks")

    # Get available semesters
    semesters = courses.values_list(
        "semester",
        flat=True
    ).distinct().order_by("semester")

    return render(
        request,
        "student/marks_year.html",
        {
            "student": student,
            "session": student.session,
            "year": year,
            "semesters": semesters,
        }
    )


from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def student_marks_semester(
    request,
    session_id,
    year,
    semester
):

    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    # Student must belong to this session
    if student.session_id != session_id:
        return redirect("student_class_test_marks")

    # Courses
    courses = Course.objects.filter(
        session_id=session_id,
        year=year,
        semester=semester
    ).select_related(
        "teacher",
        "session"
    ).order_by("course_code")

    if not courses.exists():
        return redirect(
            "student_marks_year",
            session_id=session_id,
            year=year
        )

    # ==========================================================
    # CLASS TEST + SEMESTER MARKS
    # ==========================================================

    marks = ClassTestMark.objects.filter(
        student=student,
        course__in=courses
    )

    marks_by_course = {
        mark.course_id: mark
        for mark in marks
    }

    # ==========================================================
    # SEMESTER SUMMARY
    # ==========================================================

    total_credit = Decimal("0")
    total_credit_grade_point = Decimal("0")

    # ==========================================================
    # COURSE-WISE CALCULATION
    # ==========================================================

    for course in courses:

        student_mark = marks_by_course.get(course.id)

        course.student_mark = student_mark

        # ------------------------------------------------------
        # CT MARKS
        # ------------------------------------------------------

        ct_marks = []

        if student_mark:

            if student_mark.ct1 is not None:
                ct_marks.append(
                    Decimal(str(student_mark.ct1))
                )

            if student_mark.ct2 is not None:
                ct_marks.append(
                    Decimal(str(student_mark.ct2))
                )

            if student_mark.ct3 is not None:
                ct_marks.append(
                    Decimal(str(student_mark.ct3))
                )

        # Highest 2 CT marks
        ct_marks = sorted(
            ct_marks,
            reverse=True
        )[:2]

        if ct_marks:
            ct_average = sum(ct_marks) / Decimal(
                len(ct_marks)
            )
        else:
            ct_average = Decimal("0")

        # ------------------------------------------------------
        # SEMESTER MARKS OUT OF 70
        # ------------------------------------------------------

        if (
            student_mark
            and student_mark.semester_marks is not None
        ):
            semester_marks = Decimal(
                str(student_mark.semester_marks)
            )
        else:
            semester_marks = Decimal("0")

        # ------------------------------------------------------
        # ATTENDANCE
        # ------------------------------------------------------

        attendance_sessions = AttendanceSession.objects.filter(
            course=course,
            is_held=True
        )

        total_classes = attendance_sessions.count()

        present_classes = AttendanceRecord.objects.filter(
            attendance_session__in=attendance_sessions,
            student=student,
            status="present"
        ).count()

        if total_classes > 0:

            attendance_percentage = (
                Decimal(present_classes)
                / Decimal(total_classes)
            ) * Decimal("100")

        else:
            attendance_percentage = Decimal("0")

        # ------------------------------------------------------
        # ATTENDANCE MARKS
        # ------------------------------------------------------

        if attendance_percentage < 50:
            attendance_marks = Decimal("0")

        elif attendance_percentage < 60:
            attendance_marks = Decimal("2")

        elif attendance_percentage < 70:
            attendance_marks = Decimal("3")

        elif attendance_percentage < 80:
            attendance_marks = Decimal("4")

        elif attendance_percentage < 90:
            attendance_marks = Decimal("4.5")

        else:
            attendance_marks = Decimal("5")

        # ------------------------------------------------------
        # TOTAL MARKS
        # ------------------------------------------------------

        total_marks = (
            ct_average
            + semester_marks
            + attendance_marks
        )

        # ------------------------------------------------------
        # GRADE POINT
        # ------------------------------------------------------

        if total_marks >= 80:
            grade_point = Decimal("4.00")
            letter_grade = "A+"

        elif total_marks >= 75:
            grade_point = Decimal("3.75")
            letter_grade = "A"

        elif total_marks >= 70:
            grade_point = Decimal("3.50")
            letter_grade = "A-"

        elif total_marks >= 65:
            grade_point = Decimal("3.25")
            letter_grade = "B+"

        elif total_marks >= 60:
            grade_point = Decimal("3.00")
            letter_grade = "B"

        elif total_marks >= 55:
            grade_point = Decimal("2.75")
            letter_grade = "B-"

        elif total_marks >= 50:
            grade_point = Decimal("2.50")
            letter_grade = "C+"

        elif total_marks >= 45:
            grade_point = Decimal("2.25")
            letter_grade = "C"

        elif total_marks >= 40:
            grade_point = Decimal("2.00")
            letter_grade = "D"

        else:
            grade_point = Decimal("0.00")
            letter_grade = "F"

        # ------------------------------------------------------
        # COURSE CREDIT
        # ------------------------------------------------------

        credit = Decimal(str(course.credit))

        credit_grade_point = credit * grade_point

        # ------------------------------------------------------
        # ATTACH VALUES TO COURSE
        # ------------------------------------------------------

        course.ct_average = round(
            ct_average,
            2
        )

        course.semester_marks = round(
            semester_marks,
            2
        )

        course.attendance_percentage = round(
            attendance_percentage,
            2
        )

        course.attendance_marks = attendance_marks

        course.total_marks = round(
            total_marks,
            2
        )

        course.grade_point = grade_point

        course.letter_grade = letter_grade

        course.credit = credit

        course.credit_grade_point = round(
            credit_grade_point,
            2
        )

        # ------------------------------------------------------
        # TGPA CALCULATION VALUES
        # ------------------------------------------------------

        total_credit += credit

        total_credit_grade_point += credit_grade_point

    # ==========================================================
    # TGPA
    # ==========================================================

    if total_credit > 0:

        tgpa = (
            total_credit_grade_point
            / total_credit
        )

    else:
        tgpa = Decimal("0.00")

    return render(
        request,
        "student/marks_semester.html",
        {
            "student": student,
            "session": student.session,
            "year": year,
            "semester": semester,
            "courses": courses,

            "total_credit": total_credit,
            "total_credit_grade_point": round(
                total_credit_grade_point,
                2
            ),
            "tgpa": round(tgpa, 2),
        }
    )
    
@login_required
def teacher_management(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    teachers = User.objects.filter(
        role="teacher"
    ).select_related("position")

    positions = Position.objects.all().order_by("name")

    position_id = request.GET.get("position")

    if position_id:
        teachers = teachers.filter(
        position_id=position_id
    )

    return render(
        request,
        "admin/teacher_management.html",
        {
            "teachers": teachers,
            "positions": positions,
        }
    )
    
@login_required
def session_management(request):
    if request.user.role != "admin":
        return redirect("dashboard")

    sessions = Session.objects.all().order_by("-year")

    return render(
        request,
        "admin/session_management.html",
        {
            "sessions": sessions,
        }
    )
    
    
@login_required
def create_session(request):
    if request.user.role !="admin":
        return redirect("dashboard")
    if request.method =="POST":
        form = SessionForm(request.POST)
        if form.is_valid():
          form.save()
        
          return redirect("session_management")
    
    else :
        form = SessionForm()
        
    return render(
        request,
        "admin/create_session.html",
        {
            "form":form,
        }
    )
    
@login_required
def session_students (request,session_id):
    if request.user. role !="admin":
        return redirect("dashboard")
    
    session = get_object_or_404(
        Session,
        id=session_id
    )
    
    students = User.objects.filter(
        role = "student",
        session= session
    ).order_by("id")
    
    return render(
        request,
        "admin/session_students.html",
        {
            "session":session,
            "students": students,
        }
    )
    
    
@login_required
def edit_session(request, session_id):
    if request.user.role !="admin":
        return redirect("dashboard")
    
    session = get_object_or_404(
        Session,
        id = session_id
    )
    if request.method == "POST":
        form = SessionForm(
            request.POST,
            instance=session
        )
        
        if form.is_valid():
            form.save()
            
            return redirect("session_management")
            
    else:
        form = SessionForm(
            instance=session
        )
    return render(
        request,
        "admin/edit_session.html",
        {
            "form":form,
            "session":session
        }
    )

@login_required
def delete_session (request,session_id):
    if request.user.role!="admin":
        return redirect("dashboard")
    
    session = get_object_or_404(
        Session,
        id= session_id
    )
    
    if request.method == "POST":
        session.delete()
        
        return redirect("session_management")
    
    return render(
        request,
        "admin/delete_session.html",
        {
            "session": session,
        }
    )
    
@login_required
def course_management(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    courses = Course.objects.select_related(
        "session",
        "teacher",
    ).order_by(
        "id"
    )
    
    session_id = request.GET.get("session")
    year = request.GET.get("year")
    semester = request.GET.get("semester")
    teacher_id = request.GET.get("teacher")
    
    if session_id :
        courses = courses.filter(session_id=session_id)
    if year:
        courses = courses.filter(year=year)
        
    if semester:
        courses=courses.filter(semester=semester)
    
    if teacher_id:
        courses=courses.filter(teacher_id=teacher_id)
        
    sessions = Session.objects.all().order_by("-year")
    teachers = User.objects.filter(
        role = "teacher"
    ).order_by(
        "first_name",
        "last_name"
    )
    

    return render(
        request,
        "admin/course_management.html",
        {
            "courses": courses,
            "sessions":sessions,
            "teachers":teachers,
            "year_choices": Course.YEAR_CHOICES,
            "semester_choices": Course.SEMESTER_CHOICES,
            "selected_session": session_id,
            "selected_year": year,
            "selected_semester":semester,
            "selected_teacher": teacher_id,
            
            
        }
    )
    
    
@login_required
def create_course(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():

            course = form.save()

            # ==========================================
            # NOTIFY ASSIGNED TEACHER
            # ==========================================

            if course.teacher:

                Notification.objects.create(
                    recipient=course.teacher,
                    title="New Course Assigned",
                    message=(
                        f"You have been assigned a new course: "
                        f"{course.course_code} - {course.course_name}."
                    ),
                    notification_type="course_assigned",
                )

            return redirect("course_management")

    else:

        form = CourseForm()

    return render(
        request,
        "admin/create_course.html",
        {
            "form": form,
        }
    )
    
    
@login_required
def edit_course(request, course_id):

    if request.user.role != "admin":
        return redirect("dashboard")

    course = get_object_or_404(
        Course,
        id=course_id
    )

    # ==========================================
    # OLD TEACHER
    # ==========================================

    old_teacher_id = course.teacher_id

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            instance=course
        )

        if form.is_valid():

            course = form.save()

            # ==========================================
            # TEACHER CHANGED
            # ==========================================

            if (
                course.teacher
                and course.teacher_id != old_teacher_id
            ):

                Notification.objects.create(
                    recipient=course.teacher,
                    title="Course Assigned",
                    message=(
                        f"You have been assigned the course "
                        f"{course.course_code} - "
                        f"{course.course_name}."
                    ),
                    notification_type="course_assigned",
                )

            return redirect("course_management")

    else:

        form = CourseForm(
            instance=course
        )

    return render(
        request,
        "admin/edit_course.html",
        {
            "form": form,
            "course": course,
        }
    )
    
    
@login_required
def delete_course(reqeuest,course_id):
    if reqeuest.user.role != "admin":
        return redirect("dashboard")
    
    course = get_object_or_404(
        Course,
        id = course_id
    )
    if reqeuest.method == "POST":
        course.delete()
        
        return redirect("course_management")
    
    return render(
        reqeuest,
        "admin/delete_course.html",
        
            {
                "course":course,
            }
        
    )
    
@login_required
def student_profile(request):

    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    if request.method == "POST":

        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=student
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("student_profile")

        else:

            messages.error(
                request,
                "Please correct the errors below."

            )

    else:

        form = StudentProfileForm(
            instance=student
        )

    return render(
        request,
        "student/profile.html",
        {
            "student": student,
            "form": form,
        }
    )
    


@login_required
def student_course_attendance(request, course_id):

    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    # Student's own session-এর course হতে হবে
    course = Course.objects.filter(
        id=course_id,
        session=student.session
    ).first()

    if not course:
        return redirect("student_courses")

    # বর্তমানে active এবং held attendance class
    attendance_sessions = AttendanceSession.objects.filter(
        course=course,
        is_held=True,
        is_active=True
    ).order_by("class_number")

    # POST = Code verification
    if request.method == "POST":

        code = request.POST.get("code", "").strip().upper()

        attendance = attendance_sessions.filter(
            code=code
        ).first()

        if not attendance:
            return render(
                request,
                "student/attendance_code.html",
                {
                    "student": student,
                    "course": course,
                    "attendance_sessions": attendance_sessions,
                    "error": "Invalid attendance code."
                }
            )

        # Check expiry
        if timezone.now() > attendance.expires_at:

            return render(
                request,
                "student/attendance_code.html",
                {
                    "student": student,
                    "course": course,
                    "attendance_sessions": attendance_sessions,
                    "error": "This attendance code has expired."
                }
            )

        # Code correct → Face Verification
        return redirect(
            "student_face_verification",
            attendance_id=attendance.id
        )

    return render(
        request,
        "student/attendance_code.html",
        {
            "student": student,
            "course": course,
            "attendance_sessions": attendance_sessions,
        }
    )


@login_required
def verify_attendance_network(request, course_id):

    if request.user.role != "student" or request.method != "POST":
        return JsonResponse({
            "success": False,
            "network_verified": False,
            "message": "This attendance request is not valid."
        }, status=400)

    code = request.POST.get("code", "").strip().upper()
    attendance = AttendanceSession.objects.filter(
        course_id=course_id,
        code=code,
        course__session=request.user.session,
        is_held=True,
        is_active=True
    ).select_related("course").first()

    if not attendance or timezone.now() > attendance.expires_at:
        return JsonResponse({
            "success": False,
            "network_verified": False,
            "message": "This attendance session is no longer active."
        }, status=400)

    student_network = get_request_network_identifier(request)

    if not student_network or not attendance.network_identifier:
        return JsonResponse({
            "success": False,
            "network_verified": False,
            "message": "Network verification could not be completed. Please try again."
        }, status=400)

    if student_network != attendance.network_identifier:
        return JsonResponse({
            "success": False,
            "network_verified": False,
            "message": (
                "✗ Network Verification Failed<br>"
                "Please connect to the same Wi-Fi network as the teacher and try again."
            )
        })

    request.session[f"network_verified_{attendance.id}"] = True

    return JsonResponse({
        "success": True,
        "network_verified": True,
        "message": (
            "✓ Network Verified<br>"
            "You are connected to the same network as the teacher."
        )
    })


@login_required
def student_face_verification(request, attendance_id):

    # ==========================================
    # ONLY STUDENT CAN ACCESS
    # ==========================================

    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    # ==========================================
    # GET ACTIVE ATTENDANCE SESSION
    # ==========================================

    attendance = AttendanceSession.objects.filter(
        id=attendance_id,
        course__session=student.session,
        is_held=True,
        is_active=True
    ).select_related(
        "course",
        "course__session"
    ).first()

    if not attendance:
        return redirect("student_courses")

    network_verified_key = f"network_verified_{attendance.id}"

    if not request.session.get(network_verified_key, False):
        if request.method == "POST":
            return JsonResponse({
                "success": False,
                "message": (
                    "Network verification is required before face verification."
                )
            }, status=403)

        return redirect(
            "student_course_attendance",
            course_id=attendance.course_id
        )

    # ==========================================
    # CHECK EXPIRY
    # ==========================================

    if timezone.now() > attendance.expires_at:

        return render(
            request,
            "student/face_verification.html",
            {
                "student": student,
                "attendance": attendance,
                "course": attendance.course,
                "error": "Attendance session has expired."
            }
        )

    # ==========================================
    # CHECK FACE LOCK PHOTO
    # ==========================================

    if not student.face_image:

        return render(
            request,
            "student/face_verification.html",
            {
                "student": student,
                "attendance": attendance,
                "course": attendance.course,
                "error": (
                    "Face Lock photo is not set. "
                    "Please set your Face Lock photo from your profile."
                )
            }
        )

    # ==========================================
    # POST = VERIFY LIVE FACE
    # ==========================================

    if request.method == "POST":

        image_data = request.POST.get("image")

        if not image_data:
            return JsonResponse({
                "success": False,
                "message": "No face image received."
            })

        try:

            # ==========================================
            # 1. DECODE CAMERA IMAGE
            # ==========================================

            if "," in image_data:
                image_data = image_data.split(",", 1)[1]

            image_bytes = base64.b64decode(image_data)

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            live_image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if live_image is None:

                return JsonResponse({
                    "success": False,
                    "message": "Could not read camera image."
                })

            # ==========================================
            # 2. CONVERT BGR → RGB
            # ==========================================

            live_image_rgb = cv2.cvtColor(
                live_image,
                cv2.COLOR_BGR2RGB
            )

            # Make sure image is uint8
            live_image_rgb = np.asarray(
                live_image_rgb,
                dtype=np.uint8
            )

            # Make contiguous
            live_image_rgb = np.ascontiguousarray(
                live_image_rgb
            )

            # ==========================================
            # 3. DETECT LIVE FACE
            # ==========================================

            live_locations = face_recognition.face_locations(
                live_image_rgb
            )

            # No face
            if len(live_locations) == 0:

                return JsonResponse({
                    "success": False,
                    "message": (
                        "No face detected. "
                        "Please position your face clearly."
                    )
                })

            # Multiple faces
            if len(live_locations) > 1:

                return JsonResponse({
                    "success": False,
                    "message": (
                        "Multiple faces detected. "
                        "Only one person should be visible."
                    )
                })

            # ==========================================
            # 4. ENCODE LIVE FACE
            # ==========================================

            live_encodings = face_recognition.face_encodings(
                live_image_rgb,
                live_locations
            )

            if not live_encodings:

                return JsonResponse({
                    "success": False,
                    "message": (
                        "Could not encode the detected face."
                    )
                })

            live_encoding = live_encodings[0]

            # ==========================================
            # 5. LOAD SAVED FACE LOCK PHOTO
            # ==========================================

            stored_image = cv2.imread(
                student.face_image.path,
                cv2.IMREAD_COLOR
            )

            if stored_image is None:

                return JsonResponse({
                    "success": False,
                    "message": (
                        "Could not read your saved "
                        "Face Lock photo."
                    )
                })

            # ==========================================
            # 6. CONVERT SAVED IMAGE BGR → RGB
            # ==========================================

            stored_image_rgb = cv2.cvtColor(
                stored_image,
                cv2.COLOR_BGR2RGB
            )

            stored_image_rgb = np.asarray(
                stored_image_rgb,
                dtype=np.uint8
            )

            stored_image_rgb = np.ascontiguousarray(
                stored_image_rgb
            )

            # ==========================================
            # 7. DETECT FACE IN SAVED PHOTO
            # ==========================================

            stored_locations = face_recognition.face_locations(
                stored_image_rgb
            )

            # No face in saved photo
            if len(stored_locations) == 0:

                return JsonResponse({
                    "success": False,
                    "message": (
                        "No face was detected in your "
                        "saved Face Lock photo."
                    )
                })

            # Multiple faces in saved photo
            if len(stored_locations) > 1:

                return JsonResponse({
                    "success": False,
                    "message": (
                        "Your saved Face Lock photo "
                        "contains multiple faces."
                    )
                })

            # ==========================================
            # 8. ENCODE SAVED FACE
            # ==========================================

            stored_encodings = face_recognition.face_encodings(
                stored_image_rgb,
                stored_locations
            )

            if not stored_encodings:

                return JsonResponse({
                    "success": False,
                    "message": (
                        "Could not process your saved "
                        "Face Lock photo."
                    )
                })

            stored_encoding = stored_encodings[0]

            # ==========================================
            # 9. COMPARE FACES
            # ==========================================

            distance = face_recognition.face_distance(
                [stored_encoding],
                live_encoding
            )[0]

            # Lower = more similar
            MATCH_THRESHOLD = 0.50

            matched = distance <= MATCH_THRESHOLD

            print(
                "FACE DISTANCE:",
                round(float(distance), 4)
            )

            # ==========================================
            # 10. FACE DOES NOT MATCH
            # ==========================================

            if not matched:

                return JsonResponse({
                    "success": False,
                    "message": (
                        "Face does not match your "
                        "Face Lock photo. "
                        "Please try again."
                    ),
                    "distance": round(
                        float(distance),
                        4
                    )
                })

            # ==========================================
            # 11. FACE MATCHED
            # ==========================================

            AttendanceRecord.objects.update_or_create(
                attendance_session=attendance,
                student=student,
                defaults={
                    "status": "present",
                    "method": "face",
                    "verified_at": timezone.now(),
                }
            )

            request.session.pop(network_verified_key, None)

            # ==========================================
            # 12. SUCCESS RESPONSE
            # ==========================================

            return JsonResponse({
                "success": True,
                "message": (
                    "Face verified successfully. "
                    "Attendance marked Present."
                ),
                "distance": round(
                    float(distance),
                    4
                )
            })

        # ==========================================
        # ERROR HANDLING
        # ==========================================

        except Exception as e:

            import traceback

            print(
                "\n========== "
                "FACE VERIFICATION ERROR "
                "=========="
            )

            print(str(e))

            traceback.print_exc()

            print(
                "====================================="
                "============\n"
            )

            return JsonResponse({
                "success": False,
                "message": (
                    f"Face verification error: {str(e)}"
                )
            })

    # ==========================================
    # GET = SHOW CAMERA PAGE
    # ==========================================

    return render(
        request,
        "student/face_verification.html",
        {
            "student": student,
            "attendance": attendance,
            "course": attendance.course,
        }
    )
    
    
@login_required
def student_course_attendance_history(request, course_id):
    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user

    course = Course.objects.filter(
        id=course_id,
        session=student.session
    ).select_related("teacher", "session").first()

    if not course:
        return redirect("student_courses")

    attendance_sessions = AttendanceSession.objects.filter(
        course=course,
        is_held=True
    ).order_by("class_number")

    records = AttendanceRecord.objects.filter(
        attendance_session__in=attendance_sessions,
        student=student
    )

    records_map = {
        record.attendance_session_id: record
        for record in records
    }

    present_count = 0
    absent_count = 0

    for attendance in attendance_sessions:

        attendance.student_record = records_map.get(
            attendance.id
        )

        if attendance.student_record:

            if attendance.student_record.status == "present":
                present_count += 1

            elif attendance.student_record.status == "absent":
                absent_count += 1

    total_classes = attendance_sessions.count()

    percentage = (
        (present_count / total_classes) * 100
        if total_classes > 0
        else 0
    )

    return render(
        request,
        "student/course_attendance_history.html",
        {
            "student": student,
            "course": course,
            "session": course.session,
            "year": course.year,
            "semester": course.semester,
            "attendance_sessions": attendance_sessions,
            "present_count": present_count,
            "absent_count": absent_count,
            "total_classes": total_classes,
            "percentage": round(percentage, 2),
        }
    )
    
@login_required
def teacher_profile(request):
    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = User.objects.select_related(
        "position"
    ).get(id=request.user.id)

    return render(
        request,
        "teacher/profile.html",
        {
            "teacher": teacher,
        }
    )
    

@login_required
def teacher_edit_profile(request):
    if request.user.role != "teacher":
        return redirect("dashboard")

    teacher = request.user

    if request.method == "POST":

        teacher.first_name = request.POST.get("first_name", "").strip()
        teacher.last_name = request.POST.get("last_name", "").strip()
        teacher.gender = request.POST.get("gender") or None
        teacher.date_of_birth = request.POST.get("date_of_birth") or None
        teacher.address = request.POST.get("address", "").strip()

        if request.FILES.get("profile_image"):
            teacher.profile_image = request.FILES["profile_image"]

        teacher.save()

        return redirect("teacher_profile")

    return render(
        request,
        "teacher/edit_profile.html",
        {
            "teacher": teacher,
        }
    )
    
    
@login_required
def admin_delete_student(request, student_id):

    if request.user.role != "admin":
        return redirect("dashboard")

    student = User.objects.filter(
        id=student_id,
        role="student"
    ).first()

    if not student:
        return redirect("student_management")

    if request.method == "POST":
        student.delete()
        return redirect("student_management")

    return redirect("student_management")



@login_required
def admin_notice_list(request):
    if request.user.role != "admin":
        return redirect("dashboard")

    notices = Notice.objects.all().order_by("-created_at")

    return render(
        request,
        "admin/notice_list.html",
        {
            "notices": notices,
        }
    )
    
    
@login_required
def admin_notice_add(request):
    if request.user.role != "admin":
        return redirect("dashboard")

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        message = request.POST.get("message", "").strip()
        pdf_file = request.FILES.get("pdf_file")
        image = request.FILES.get("image")

        is_active = request.POST.get("is_active") == "on"

        if not title:
            return render(
                request,
                "admin/notice_add.html",
                {"error": "Notice title is required."}
            )

        notice = Notice.objects.create(
            title=title,
            message=message,
            pdf_file=pdf_file,
            image=image,
            is_active=is_active,
        )

   

        if notice.is_active:
        
            recipients = User.objects.filter(
        role__in=["teacher", "student"]
    )

            Notification.objects.bulk_create([
                Notification(
                    recipient=user,
                    title="New Notice",
                    message=f"A new notice has been published: {notice.title}",
                    notification_type="notice",
                )
                for user in recipients
            ])

        return redirect("admin_notice_list")

    return render(request, "admin/notice_add.html")
    
    
@login_required
def admin_notice_edit(request, notice_id):
    if request.user.role != "admin":
        return redirect("dashboard")

    notice = Notice.objects.filter(id=notice_id).first()

    if not notice:
        return redirect("admin_notice_list")

    if request.method == "POST":

        notice.title = request.POST.get("title", "").strip()
        notice.message = request.POST.get("message", "").strip()

        if request.FILES.get("pdf_file"):
            notice.pdf_file = request.FILES["pdf_file"]

        if request.FILES.get("image"):
            notice.image = request.FILES["image"]

        notice.is_active = request.POST.get("is_active") == "on"

        notice.save()

        return redirect("admin_notice_list")

    return render(
        request,
        "admin/notice_edit.html",
        {
            "notice": notice,
        }
    )
    
    
@login_required
def admin_notice_delete(request, notice_id):
    if request.user.role != "admin":
        return redirect("dashboard")

    notice = Notice.objects.filter(id=notice_id).first()

    if not notice:
        return redirect("admin_notice_list")

    if request.method == "POST":
        notice.delete()

    return redirect("admin_notice_list")


@login_required
def teacher_notices(request):
    if request.user.role != "teacher":
        return redirect("dashboard")

    notices = Notice.objects.filter(
        is_active=True
    ).order_by("-created_at")

    return render(
        request,
        "teacher/notices.html",
        {
            "notices": notices,
        }
    )
    
@login_required
def teacher_notifications(request):
    if request.user.role != "teacher":
        return redirect("dashboard")

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")

    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return render(
        request,
        "teacher/notifications.html",
        {
            "notifications": notifications,
        }
    )
    
    
@login_required
def student_notifications(request):
    if request.user.role != "student":
        return redirect("dashboard")

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")

    # সব unread notification read হয়ে যাবে
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return render(
        request,
        "student/notifications.html",
        {
            "notifications": notifications
        }
    )
    
    
@login_required
def admin_delete_teacher(request, teacher_id):

    if request.user.role != "admin":
        return redirect("dashboard")

    teacher = get_object_or_404(
        User,
        id=teacher_id,
        role="teacher"
    )

    if request.method == "POST":
        teacher.delete()

    return redirect("teacher_management")


@login_required
def admin_teacher_profile(request, teacher_id):

    if request.user.role != "admin":
        return redirect("dashboard")

    teacher = get_object_or_404(
        User,
        id=teacher_id,
        role="teacher"
    )

    return render(
        request,
        "admin/teacher_profile.html",
        {
            "teacher": teacher
        }
    )
    
    
@login_required
def admin_bus_notice_add(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    if request.method == "POST":

        title = request.POST.get("title")
        message = request.POST.get("message")
        pdf_file = request.FILES.get("pdf_file")
        image = request.FILES.get("image")

        BusNotice.objects.create(
            title=title,
            message=message,
            pdf_file=pdf_file,
            image=image,
            is_active=True
        )

        return redirect("admin_bus_notice_list")

    return render(
        request,
        "admin/bus_notice_add.html"
    )
    
    
@login_required
def admin_bus_notice_list(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    bus_notices = BusNotice.objects.all().order_by("-created_at")

    return render(
        request,
        "admin/bus_notice_list.html",
        {
            "bus_notices": bus_notices
        }
    )
    
    
@login_required
def teacher_bus_notices(request):

    if request.user.role != "teacher":
        return redirect("dashboard")

    bus_notices = BusNotice.objects.filter(
        is_active=True
    ).order_by("-created_at")

    return render(
        request,
        "teacher/bus_notices.html",
        {
            "bus_notices": bus_notices
        }
    )
    
    
@login_required
def student_bus_notices(request):

    if request.user.role != "student":
        return redirect("dashboard")

    bus_notices = BusNotice.objects.filter(
        is_active=True
    ).order_by("-created_at")

    return render(
        request,
        "student/bus_notices.html",
        {
            "bus_notices": bus_notices
        }
    )
    
    
@login_required
def admin_position_list(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    positions = Position.objects.all().order_by("name")

    return render(
        request,
        "admin/position_list.html",
        {
            "positions": positions
        }
    )
    
    
@login_required
def admin_position_add(request):
    if request.user.role!="admin":
        return redirect("dashboard")
    if request.method == "POST":
        name = request.POST.get("name","").strip()
        if name :
            Position.objects.create(
                name=name
            )
            return redirect("admin_position_list")
        
    return render(
            request,
            "admin/position_add.html"
        )
        
@login_required
def admin_position_edit(request,position_id):
    if request.user.role != "admin":
        return redirect("dashboard")
    position = get_object_or_404(
        Position,
        id = position_id
    )
    
    if request.method == "POST":
        name = request.POST.get("name","").strip()
        if name :
            position.name = name
            position.save()
            return redirect("admin_position_list")
        
    return render(
            request,
            "admin/position_edit.html",
            {
                "position":position
            }
        )
    
    
@login_required
def admin_position_delete(request,position_id):
    if request.user.role !="admin":
        return redirect("dashboard")
    position = get_object_or_404(
        Position,
        id = position_id
    )
    if request.method == "POST":
        position.delete()
    
    return redirect("admin_position_list")


@login_required
def semester_question_pattern_list(request):
    patterns = SemesterQuestionPattern.objects.select_related(
        "course"
    ).order_by(
        "course__session__year",
        "course__year",
        "course__semester",
        "course__course_code",
    )

    return render(
        request,
        "core/semester_question_pattern_list.html",
        {
            "patterns": patterns,
        }
    )
    
    
@login_required
def add_semester_question_pattern(request):

    if request.method == "POST":
        form = SemesterQuestionPatternForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Semester question pattern added successfully."
            )

            return redirect(
                "semester_question_pattern_list"
            )

    else:
        form = SemesterQuestionPatternForm()

    return render(
        request,
        "core/add_semester_question_pattern.html",
        {
            "form": form,
        }
    )
    
    
@login_required
def semester_question_set_list(request, pattern_id):

    pattern = get_object_or_404(
        SemesterQuestionPattern,
        id=pattern_id
    )

    question_sets = pattern.question_sets.all().order_by(
        "order"
    )

    return render(
        request,
        "core/semester_question_set_list.html",
        {
            "pattern": pattern,
            "question_sets": question_sets,
        }
    )
    
    
    
@login_required
def add_semester_question_set(request, pattern_id):

    pattern = get_object_or_404(
        SemesterQuestionPattern,
        id=pattern_id
    )

    if request.method == "POST":
        form = SemesterQuestionSetForm(request.POST)

        if form.is_valid():
            question_set = form.save(commit=False)
            question_set.pattern = pattern
            question_set.save()

            messages.success(
                request,
                "Question set added successfully."
            )

            return redirect(
                "semester_question_set_list",
                pattern_id=pattern.id
            )

    else:
        form = SemesterQuestionSetForm()

    return render(
        request,
        "core/add_semester_question_set.html",
        {
            "form": form,
            "pattern": pattern,
        }
    )
    
@login_required
def semester_sub_question_list(request, set_id):

    question_set = get_object_or_404(
        SemesterQuestionSet,
        id=set_id
    )

    sub_questions = question_set.subquestions.all().order_by(
        "order"
    )

    return render(
        request,
        "core/semester_sub_question_list.html",
        {
            "question_set": question_set,
            "sub_questions": sub_questions,
        }
    )
    
    
@login_required
def add_semester_sub_question(request, set_id):

    question_set = get_object_or_404(
        SemesterQuestionSet,
        id=set_id
    )

    if request.method == "POST":
        form = SemesterSubQuestionForm(request.POST)

        if form.is_valid():
            sub_question = form.save(commit=False)
            sub_question.question_set = question_set
            sub_question.save()

            messages.success(
                request,
                "Sub-question added successfully."
            )

            return redirect(
                "semester_sub_question_list",
                set_id=question_set.id
            )

    else:
        form = SemesterSubQuestionForm()

    return render(
        request,
        "core/add_semester_sub_question.html",
        {
            "form": form,
            "question_set": question_set,
        }
    )
    
    
@login_required
def add_semester_sub_question_mark(request, sub_question_id):

    sub_question = get_object_or_404(
        SemesterSubQuestion,
        id=sub_question_id
    )

    mark, created = SemesterSubQuestionMark.objects.get_or_create(
        sub_question=sub_question
    )

    if request.method == "POST":
        form = SemesterSubQuestionMarkForm(
            request.POST,
            instance=mark
        )

        if form.is_valid():
            saved_mark = form.save(commit=False)

            if (
                saved_mark.obtained_marks >
                sub_question.marks
            ):
                form.add_error(
                    "obtained_marks",
                    "Obtained marks cannot exceed question marks."
                )
            else:
                saved_mark.save()

                messages.success(
                    request,
                    "Marks saved successfully."
                )

                return redirect(
                    "semester_sub_question_list",
                    set_id=sub_question.question_set.id
                )

    else:
        form = SemesterSubQuestionMarkForm(
            instance=mark
        )

    return render(
        request,
        "core/add_semester_sub_question_mark.html",
        {
            "form": form,
            "sub_question": sub_question,
        }
    )
    
    
@login_required
def semester_sub_question_mark_list(request, sub_question_id):
    sub_question = get_object_or_404(
        SemesterSubQuestion,
        id=sub_question_id
    )

    marks = SemesterSubQuestionMark.objects.filter(
        sub_question=sub_question
    ).select_related("student").order_by(
        "student__email"
    )

    return render(
        request,
        "core/semester_sub_question_mark_list.html",
        {
            "sub_question": sub_question,
            "marks": marks,
        }
    )


@login_required
def teacher_semester_set_marks(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    pattern = SemesterQuestionPattern.objects.filter(
        course=course
    ).first()

    students = User.objects.filter(
        role="student",
        session=course.session
    ).order_by(
        "roll",
        "first_name",
        "last_name",
        "email"
    )

    return render(
        request,
        "core/teacher_semester_set_marks.html",
        {
            "course": course,
            "pattern": pattern,
            "students": students,
        }
    )


@login_required
def teacher_semester_student_sets(request, course_id, student_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    student = get_object_or_404(
        User,
        id=student_id,
        role="student",
        session=course.session
    )

    pattern = SemesterQuestionPattern.objects.filter(
        course=course
    ).first()

    question_sets = (
        pattern.question_sets.all().order_by("order")
        if pattern
        else []
    )

    set_rows = []

    for question_set in question_sets:
        obtained_total = sum(
            (
                mark.obtained_marks
                for mark in SemesterSubQuestionMark.objects.filter(
                    student=student,
                    sub_question__question_set=question_set
                )
            ),
            Decimal("0")
        )

        set_rows.append(
            {
                "question_set": question_set,
                "obtained_total": obtained_total,
            }
        )

    return render(
        request,
        "core/teacher_semester_student_sets.html",
        {
            "course": course,
            "student": student,
            "pattern": pattern,
            "question_sets": question_sets,
            "set_rows": set_rows,
        }
    )


@login_required
def teacher_semester_set_detail(request, course_id, set_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    question_set = get_object_or_404(
        SemesterQuestionSet,
        id=set_id,
        pattern__course=course
    )

    students = User.objects.filter(
        role="student",
        session=course.session
    ).order_by("roll", "first_name", "last_name")

    return render(
        request,
        "core/teacher_semester_set_detail.html",
        {
            "course": course,
            "question_set": question_set,
            "students": students,
        }
    )


@login_required
def teacher_semester_subquestion_marks(
    request,
    course_id,
    set_id,
    sub_question_id
):
    course = get_object_or_404(
        Course,
        id=course_id
    )

    question_set = get_object_or_404(
        SemesterQuestionSet,
        id=set_id,
        pattern__course=course
    )

    sub_question = get_object_or_404(
        SemesterSubQuestion,
        id=sub_question_id,
        question_set=question_set
    )

    students = User.objects.filter(
        role="student",
        session=course.session
    ).order_by("roll")

    existing_marks = {}

    for mark in SemesterSubQuestionMark.objects.filter(
        sub_question=sub_question
    ):
        existing_marks[mark.student_id] = mark.obtained_marks

    if request.method == "POST":

        for student in students:
            value = request.POST.get(f"marks_{student.id}")

            if value is None or value == "":
                continue

            try:
                parsed_value = Decimal(str(value))
            except InvalidOperation:
                messages.error(
                    request,
                    f"Invalid number entered for {student.get_full_name() or student.username}."
                )
                return redirect(
                    "teacher_semester_subquestion_marks",
                    course_id=course.id,
                    set_id=question_set.id,
                    sub_question_id=sub_question.id
                )

            if parsed_value < 0:
                messages.error(
                    request,
                    f"Marks cannot be less than 0 for {student.get_full_name() or student.username}."
                )
                return redirect(
                    "teacher_semester_subquestion_marks",
                    course_id=course.id,
                    set_id=question_set.id,
                    sub_question_id=sub_question.id
                )

            if parsed_value > sub_question.marks:
                messages.error(
                    request,
                    f"Marks for {student.get_full_name() or student.username} cannot exceed {sub_question.marks}."
                )
                return redirect(
                    "teacher_semester_subquestion_marks",
                    course_id=course.id,
                    set_id=question_set.id,
                    sub_question_id=sub_question.id
                )

            SemesterSubQuestionMark.objects.update_or_create(
                student=student,
                sub_question=sub_question,
                defaults={
                    "obtained_marks": parsed_value
                }
            )

        messages.success(
            request,
            f"Marks saved successfully for {sub_question.question_label}."
        )

        return redirect(
            "teacher_semester_subquestion_marks",
            course_id=course.id,
            set_id=question_set.id,
            sub_question_id=sub_question.id
        )

    student_rows = []

    for student in students:
        student_rows.append({
            "student": student,
            "mark": existing_marks.get(student.id, "")
        })

    return render(
        request,
        "core/teacher_semester_subquestion_marks.html",
        {
            "course": course,
            "question_set": question_set,
            "sub_question": sub_question,
            "student_rows": student_rows,
        }
    )


@login_required
def teacher_semester_student_set_marks(
    request,
    course_id,
    set_id,
    student_id
):
    course = get_object_or_404(
        Course,
        id=course_id
    )

    question_set = get_object_or_404(
        SemesterQuestionSet,
        id=set_id,
        pattern__course=course
    )

    student = get_object_or_404(
        User,
        id=student_id,
        role="student",
        session=course.session
    )

    sub_questions = question_set.sub_questions.all().order_by("order")

    existing_marks = {}
    marks = SemesterSubQuestionMark.objects.filter(
        student=student,
        sub_question__question_set=question_set
    )

    for mark in marks:
        existing_marks[mark.sub_question_id] = mark.obtained_marks

    if request.method == "POST":
        invalid_entries = []
        valid_entries = {}

        for sub_question in sub_questions:
            raw_value = request.POST.get(f"marks_{sub_question.id}")

            if raw_value is None or raw_value == "":
                continue

            try:
                parsed_value = Decimal(str(raw_value))
            except InvalidOperation:
                invalid_entries.append(
                    f"{sub_question.question_label} has an invalid number."
                )
                continue

            if parsed_value < 0:
                invalid_entries.append(
                    f"{sub_question.question_label} cannot be lower than 0."
                )
                continue

            if parsed_value > sub_question.marks:
                invalid_entries.append(
                    f"{sub_question.question_label} cannot exceed {sub_question.marks}."
                )
                continue

            valid_entries[sub_question.id] = parsed_value

        if invalid_entries:
            for message_text in invalid_entries:
                messages.error(request, message_text)
            return render(
                request,
                "core/teacher_semester_student_set_marks.html",
                {
                    "course": course,
                    "question_set": question_set,
                    "student": student,
                    "sub_question_rows": [
                        {
                            "sub_question": sub_question,
                            "obtained": existing_marks.get(sub_question.id, ""),
                        }
                        for sub_question in sub_questions
                    ],
                    "total_obtained": sum(
                        (value for value in existing_marks.values()),
                        Decimal("0")
                    )
                }
            )

        for sub_question_id, value in valid_entries.items():
            SemesterSubQuestionMark.objects.update_or_create(
                student=student,
                sub_question_id=sub_question_id,
                defaults={
                    "obtained_marks": value
                }
            )

        messages.success(
            request,
            f"Marks saved successfully for {student.get_full_name() or student.username}."
        )

        return redirect(
            "teacher_semester_student_sets",
            course_id=course.id,
            student_id=student.id
        )

    sub_question_rows = []
    total_obtained = Decimal("0")

    for sub_question in sub_questions:
        obtained = existing_marks.get(sub_question.id, "")
        if obtained != "":
            total_obtained += obtained

        sub_question_rows.append({
            "sub_question": sub_question,
            "obtained": obtained,
        })

    return render(
        request,
        "core/teacher_semester_student_set_marks.html",
        {
            "course": course,
            "question_set": question_set,
            "student": student,
            "sub_question_rows": sub_question_rows,
            "total_obtained": total_obtained,
        }
    )



     
        
    




