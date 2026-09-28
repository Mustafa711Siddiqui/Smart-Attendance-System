from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    Session,
    Position,
    Course,
    ClassTestMark,
    AttendanceSession,
    AttendanceRecord,
    Notice,
    Notification,
    BusNotice,
    SemesterQuestionPattern,
    SemesterQuestionSet,
    SemesterSubQuestion,
    SemesterSubQuestionMark,
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
        "session",
        "position",
        "gender",
        "is_active",
    )

    list_filter = (
        "role",
        "session",
        "position",
        "gender",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
    )

    ordering = (
        "role",
        "session",
        "position",
        "email",
    )

    add_fieldsets = (

        (
            None,
            {
                "classes": ("wide",),

                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),

    )

    fieldsets = (

        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),

        (
            "Personal Information",
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "address",
                    "profile_image",
                ),
            },
        ),

        (
            "Academic Information",
            {
                "fields": (
                    "role",
                    "session",
                    "position",
                ),
            },
        ),

        (
            "Role & Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),

    )
    
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "year",
        "is_graduated",
        "created_at",
    )
    list_filter = (
        "is_graduated",
    )
    search_fields =(
        "year",
    )
    


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):

    list_display = (
        "name",
    )
    
    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "course_code",
        "course_name",
        "year",
        "semester",
        "credit",
        "session",
        "teacher",
        "created_at",
    )

    list_filter = (
        "year",
        "semester",
        "session",
        "teacher",
    )

    search_fields = (
        "course_code",
        "course_name",
    )

    ordering = (
        "session",
        "year",
        "semester",
        "course_code",
    )
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
    
        if db_field.name == "teacher":
            kwargs["queryset"] = User.objects.filter(
                role="teacher"
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )
        
@admin.register(ClassTestMark)
class ClassTestMarkAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "course",
        "ct1",
        "ct2",
        "ct3",
    )

    list_filter = (
        "course",
    )

    search_fields = (
        "student__email",
        "student__username",
        "student__first_name",
        "student__last_name",
        "course__course_code",
    )

    ordering = (
        "course",
        "student__roll",
    )
    
@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "class_number",
        "date",
        "is_held",
        "is_active",
        "code",
        "expires_at",
    )

    list_filter = (
        "is_held",
        "is_active",
        "course",
    )

    search_fields = (
        "course__course_code",
        "course__course_name",
        "code",
    )

    ordering = (
        "-date",
        "course",
        "class_number",
    )
    
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "attendance_session",
        "status",
        "method",
        "verified_at",
    )

    list_filter = (
        "status",
        "method",
        "attendance_session__course",
    )

    search_fields = (
        "student__email",
        "student__username",
        "student__first_name",
        "student__last_name",
        "attendance_session__course__course_code",
    )

    ordering = (
        "attendance_session",
        "student__roll",
    )
    
    
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
    )

    ordering = (
        "-created_at",
    )
    
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "recipient",
        "title",
        "notification_type",
        "is_read",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "is_read",
        "created_at",
    )

    search_fields = (
        "recipient__email",
        "recipient__username",
        "recipient__first_name",
        "recipient__last_name",
        "title",
        "message",
    )

    ordering = (
        "-created_at",
    )
    
    
@admin.register(BusNotice)
class BusNoticeAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
    )

    ordering = (
        "-created_at",
    )
    
    
@admin.register(SemesterQuestionPattern)
class SemesterQuestionPatternAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "total_marks",
        "created_at",
        "total_set_marks",
    )

    search_fields = (
        "course__course_code",
        "course__course_name",
    )

    readonly_fields = (
        "created_at",
        "total_set_marks",
    )

    def total_set_marks(self, obj):
        return obj.get_total_set_marks()

    total_set_marks.short_description = "Total Set Marks"


@admin.register(SemesterQuestionSet)
class SemesterQuestionSetAdmin(admin.ModelAdmin):

    list_display = (
        "pattern",
        "set_name",
        "total_marks",
        "order",
        "total_subquestion_marks",
    )

    list_filter = (
        "set_name",
    )

    search_fields = (
        "pattern__course__course_code",
        "set_name",
    )

    def total_subquestion_marks(self, obj):
        return obj.get_total_subquestion_marks()

    total_subquestion_marks.short_description = (
        "Total Sub-question Marks"
    )


@admin.register(SemesterSubQuestion)
class SemesterSubQuestionAdmin(admin.ModelAdmin):

    list_display = (
        "question_set",
        "question_label",
        "marks",
        "order",
    )

    list_filter = (
        "question_set",
    )

    search_fields = (
        "question_label",
        "question_set__set_name",
        "question_set__pattern__course__course_code",
    )


@admin.register(SemesterSubQuestionMark)
class SemesterSubQuestionMarkAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "sub_question",
        "obtained_marks",
        "maximum_marks",
        "course",
    )

    list_filter = (
        "sub_question__question_set__pattern__course",
    )

    search_fields = (
        "student__email",
        "student__username",
        "sub_question__question_label",
    )

    def maximum_marks(self, obj):
        return obj.sub_question.marks

    maximum_marks.short_description = "Maximum Marks"

    def course(self, obj):
        return (
            obj.sub_question
            .question_set
            .pattern
            .course
        )

    course.short_description = "Course"
