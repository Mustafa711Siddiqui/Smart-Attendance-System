from django.urls import path
from . import views

urlpatterns = [
    path("login/",views.login_view,name="login"),
    path("logout/",views.Logout_view,name="logout"),
    path("register/",views.register_view,name="register"),
    path("",views.home,name="home"),
    path("index/",views.index),
    path("student/dashbaord/",views.student_dashboard,name="student_dashboard"),
    path(
    "dashboard/",
    views.dashboard,
    name="dashboard"
),
path(
    "student/<int:student_id>/profile/",
    views.admin_student_profile,
    name="admin_student_profile"
),
    path("admin_dashboard/",views.admin_dashboard,name="admin_dashboard"),
    path("admin-dashboard/students/",views.student_managemnet,name="student_management"),
    path("admin-dashboard/teachers/",views.teacher_management,name="teacher_management"),
    path("admin-dashboard/sessions/",views.session_management,name="session_management"),
    path("admin-dashboard/sessions/create/",views.create_session,name="create_session"),
    path("admin-dashboard/sessions/<int:session_id>/students/",views.session_students,name="session_students"),
    path("admin-dashboard/sessions/<int:session_id>/edit/",views.edit_session,name="edit_session"),
    path("admin-dashboard/sessions/<int:session_id>delete/",views.delete_session,name="delete_session"),
    path("admin-dashboard/courses/management/",views.course_management, name="course_management"),
    path("admin-dashboard/courses/create/",views.create_course,name="create_course"),
    path("admin-dashboard/courses/<int:course_id>/edit/",views.edit_course,name="edit_course"),
    path("admin-dashboard/courses/<int:course_id>/delete/",views.delete_course,name="delete_course"),
    path("teacher_profile/",views.teacher_dashboard,name="teacher_dashboard"),
    path("teacher-dashboard/session/<int:session_id>/",views.teacher_session_courses, name="teacher_session_courses"),
    path("teacher-dashboard/session/<int:session_id>/year/<str:year>/",views.teacher_year_courses,name="teacher_year_courses"),
    path(
    "teacher-dashboard/session/<int:session_id>/year/<str:year>/semester/<str:semester>/",
    views.teacher_semester_courses,
    name="teacher_semester_courses",
    
),
    path(
    "teacher-dashboard/course/<int:course_id>/",
    views.teacher_course_detail,
    name="teacher_course_detail",
),
   path(
    "student-dashboard/courses/",
    views.student_courses,
    name="student_courses",
),
   path(
    "student-dashboard/courses/<int:session_id>/year/<str:year>/",
    views.student_year_courses,
    name="student_year_courses",
),
   
path(
    "student-dashboard/courses/<int:session_id>/year/<str:year>/semester/<str:semester>/",
    views.student_semester_courses,
    name="student_semester_courses",
),

path(
    "teacher-dashboard/course/<int:course_id>/class-test-marks/",
    views.teacher_class_test_marks,
    name="teacher_class_test_marks",
),


path(
    "student-dashboard/class-test-marks/",
    views.student_class_test_marks,
    name="student_class_test_marks",
),
path(
    "student-dashboard/class-test-marks/<int:session_id>/year/<str:year>/semester/<str:semester>/",
    views.student_marks_semester,
    name="student_marks_semester",
),
path(
    "student-dashboard/class-test-marks/<int:session_id>/year/<str:year>/",
    views.student_marks_year,
    name="student_marks_year",
),
path(
    "teacher-dashboard/attendance/<int:attendance_id>/start/",
    views.teacher_start_attendance,
    name="teacher_start_attendance",
),
path(
    "teacher-dashboard/course/<int:course_id>/create-attendance-classes/",
    views.teacher_create_attendance_classes,
    name="teacher_create_attendance_classes",
),

path(
    "teacher-dashboard/course/<int:course_id>/attendance-register/",
    views.teacher_attendance_register,
    name="teacher_attendance_register",
),

path(
    "teacher-dashboard/attendance/<int:attendance_id>/set-date/",
    views.teacher_set_attendance_date,
    name="teacher_set_attendance_date",
),
path(
    "student-dashboard/profile/",
    views.student_profile,
    name="student_profile"
),

path(
    "teacher-dashboard/attendance/<int:attendance_id>/set-timer/",
    views.teacher_set_attendance_timer,
    name="teacher_set_attendance_timer"
),
path(
    "teacher-dashboard/attendance/<int:attendance_id>/end/",
    views.teacher_end_attendance,
    name="teacher_end_attendance"
),

path(
    "student-dashboard/course/<int:course_id>/attendance/",
    views.student_course_attendance,
    name="student_course_attendance",
),

path(
    "student-dashboard/attendance/<int:attendance_id>/face/",
    views.student_face_verification,
    name="student_face_verification",
),
path(
    "student-dashboard/course/<int:course_id>/verify-network/",
    views.verify_attendance_network,
    name="verify_attendance_network",
),

path(
    "student-dashboard/course/<int:course_id>/attendance/history/",
    views.student_course_attendance_history,
    name="student_course_attendance_history",
),
path(
    "teacher-dashboard/profile/",
    views.teacher_profile,
    name="teacher_profile"
),

path(
    "teacher-dashboard/profile/edit/",
    views.teacher_edit_profile,
    name="teacher_edit_profile"
),

path(
    "student/<int:student_id>/delete/",
    views.admin_delete_student,
    name="admin_delete_student"
),

path(
    "admin-dashboard/notices/",
    views.admin_notice_list,
    name="admin_notice_list"
),

path(
    "admin-dashboard/notices/add/",
    views.admin_notice_add,
    name="admin_notice_add"
),

path(
    "admin-dashboard/notices/<int:notice_id>/edit/",
    views.admin_notice_edit,
    name="admin_notice_edit"
),

path(
    "admin-dashboard/notices/<int:notice_id>/delete/",
    views.admin_notice_delete,
    name="admin_notice_delete"
),

path(
    "teacher-dashboard/notices/",
    views.teacher_notices,
    name="teacher_notices"
),
path(
    "teacher-dashboard/notifications/",
    views.teacher_notifications,
    name="teacher_notifications"
),

path(
    "student-dashboard/notifications/",
    views.student_notifications,
    name="student_notifications"
),
path(
    "admin-dashboard/teacher/<int:teacher_id>/delete/",
    views.admin_delete_teacher,
    name="admin_delete_teacher"
),
path(
    "admin-dashboard/teacher/<int:teacher_id>/profile/",
    views.admin_teacher_profile,
    name="admin_teacher_profile"
),

path(
    "admin-dashboard/bus-notice/add/",
    views.admin_bus_notice_add,
    name="admin_bus_notice_add"
),
path(
    "admin-dashboard/bus-notice/",
    views.admin_bus_notice_list,
    name="admin_bus_notice_list"
),

path(
    "teacher-dashboard/bus-notices/",
    views.teacher_bus_notices,
    name="teacher_bus_notices"
),

path(
    "student-dashboard/bus-notices/",
    views.student_bus_notices,
    name="student_bus_notices"
),

path("admin_dashboard/positions/",views.admin_position_list,name="admin_position_list"),
path("admin_dashboard/positions/add/",views.admin_position_add,name="admin_position_add"),
path(
    "admin-dashboard/positions/<int:position_id>/edit/",
    views.admin_position_edit,
    name="admin_position_edit"
),
path("admin-dashboard/positions/<int:position_id>/delete/",views.admin_position_delete,name="admin_position_delete"),
 path(
        "semester/question-patterns/",
        views.semester_question_pattern_list,
        name="semester_question_pattern_list"
    ),

    path(
        "semester/question-patterns/add/",
        views.add_semester_question_pattern,
        name="add_semester_question_pattern"
    ),
    
path(
    "semester/question-patterns/<int:pattern_id>/sets/",
    views.semester_question_set_list,
    name="semester_question_set_list"
),

path(
    "semester/question-patterns/<int:pattern_id>/sets/add/",
    views.add_semester_question_set,
    name="add_semester_question_set"
),

    path(
        "semester/question-sets/<int:set_id>/sub-questions/",
        views.semester_sub_question_list,
        name="semester_sub_question_list"
    ),

    path(
        "semester/question-sets/<int:set_id>/sub-questions/add/",
        views.add_semester_sub_question,
        name="add_semester_sub_question"
    ),
    
    path(
    "semester/sub-questions/<int:sub_question_id>/marks/",
    views.semester_sub_question_mark_list,
    name="semester_sub_question_mark_list"
),

path(
    "semester/sub-questions/<int:sub_question_id>/marks/add/",
    views.add_semester_sub_question_mark,
    name="add_semester_sub_question_mark"
),
path(
    "teacher/course/<int:course_id>/semester-set-marks/",
    views.teacher_semester_set_marks,
    name="teacher_semester_set_marks"
),
path(
    "teacher/course/<int:course_id>/student/<int:student_id>/semester-sets/",
    views.teacher_semester_student_sets,
    name="teacher_semester_student_sets"
),
path(
    "teacher/course/<int:course_id>/semester-set/<int:set_id>/student/<int:student_id>/marks/",
    views.teacher_semester_student_set_marks,
    name="teacher_semester_student_set_marks"
),
path(
    "teacher/course/<int:course_id>/semester-set/<int:set_id>/",
    views.teacher_semester_set_detail,
    name="teacher_semester_set_detail"
),
path(
    "teacher/course/<int:course_id>/semester-set/<int:set_id>/sub-question/<int:sub_question_id>/marks/",
    views.teacher_semester_subquestion_marks,
    name="teacher_semester_subquestion_marks"
),
    
    
    
]
