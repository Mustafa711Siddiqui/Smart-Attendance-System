from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AttendanceSession, Course, Session, User


class AttendanceNetworkVerificationTests(TestCase):
	def setUp(self):
		academic_session = Session.objects.create(year="2026")
		self.student = User.objects.create_user(
			email="student@example.com",
			username="student",
			password="password",
			role="student",
			session=academic_session,
		)
		course = Course.objects.create(
			course_code="CSE101",
			course_name="Networks",
			credit="3.0",
			session=academic_session,
		)
		self.attendance = AttendanceSession.objects.create(
			course=course,
			class_number=1,
			code="ABC123",
			is_held=True,
			is_active=True,
			expires_at=timezone.now() + timedelta(minutes=10),
			network_identifier="192.168.1.0/24",
		)
		self.client.force_login(self.student)

	def test_same_subnet_sets_network_verification_flag(self):
		response = self.client.post(
			reverse("verify_attendance_network", args=[self.attendance.course_id]),
			{"code": "ABC123"},
			REMOTE_ADDR="192.168.1.25",
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()["network_verified"])
		self.assertTrue(
			self.client.session.get(f"network_verified_{self.attendance.id}")
		)

	def test_different_subnet_does_not_verify_network(self):
		response = self.client.post(
			reverse("verify_attendance_network", args=[self.attendance.course_id]),
			{"code": "ABC123"},
			REMOTE_ADDR="192.168.0.25",
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.json()["network_verified"])
		self.assertNotIn(
			f"network_verified_{self.attendance.id}",
			self.client.session,
		)

	def test_face_verification_requires_network_verification(self):
		response = self.client.get(
			reverse("student_face_verification", args=[self.attendance.id])
		)

		self.assertRedirects(
			response,
			reverse(
				"student_course_attendance",
				args=[self.attendance.course_id],
			),
		)

	def test_face_page_does_not_consume_network_verification_flag(self):
		session = self.client.session
		session[f"network_verified_{self.attendance.id}"] = True
		session.save()

		self.client.get(
			reverse("student_face_verification", args=[self.attendance.id])
		)

		self.assertTrue(
			self.client.session.get(f"network_verified_{self.attendance.id}")
		)

	def test_face_post_without_network_verification_returns_json_403(self):
		response = self.client.post(
			reverse("student_face_verification", args=[self.attendance.id]),
			{"image": "data:image/jpeg;base64,invalid"},
		)

		self.assertEqual(response.status_code, 403)
		self.assertFalse(response.json()["success"])
