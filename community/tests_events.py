from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Comment, Event, Post


class EventTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student",
            password="test-password-123",
        )
        self.staff = User.objects.create_user(
            username="event-admin",
            password="test-password-123",
            is_staff=True,
        )
        now = timezone.now()
        self.event = Event.objects.create(
            title="Rodeo Round Up",
            description="Meet us on campus.",
            starts_at=now - timedelta(hours=1),
            ends_at=now + timedelta(hours=1),
            created_by=self.staff,
        )

    def test_staff_can_create_event(self):
        self.client.force_login(self.staff)
        starts_at = (timezone.localtime() + timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M"
        )
        ends_at = (timezone.localtime() + timedelta(days=1, hours=2)).strftime(
            "%Y-%m-%dT%H:%M"
        )

        response = self.client.post(
            reverse("create_event"),
            {
                "title": "New campus celebration",
                "description": "Join the campus celebration.",
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        )

        created_event = Event.objects.get(title="New campus celebration")
        self.assertRedirects(
            response,
            reverse("event_detail", args=[created_event.pk]),
        )
        self.assertEqual(created_event.created_by, self.staff)

    def test_event_form_rejects_end_before_start(self):
        self.client.force_login(self.staff)
        starts_at = (timezone.localtime() + timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M"
        )
        ends_at = (timezone.localtime() + timedelta(hours=1)).strftime(
            "%Y-%m-%dT%H:%M"
        )

        response = self.client.post(
            reverse("create_event"),
            {
                "title": "Invalid event",
                "description": "The times are reversed.",
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "end date and time must be after the start")
        self.assertFalse(Event.objects.filter(title="Invalid event").exists())

    def test_event_pages_are_available_to_students(self):
        list_response = self.client.get(reverse("event_list"))
        detail_response = self.client.get(
            reverse("event_detail", args=[self.event.pk])
        )

        self.assertContains(list_response, self.event.title)
        self.assertContains(detail_response, self.event.description)
        self.assertContains(detail_response, "to join this event")

    def test_non_staff_cannot_create_or_close_events(self):
        self.client.force_login(self.student)
        create_response = self.client.get(reverse("create_event"))
        close_response = self.client.post(
            reverse("close_event", args=[self.event.pk])
        )

        self.assertEqual(create_response.status_code, 302)
        self.assertEqual(close_response.status_code, 302)
        self.assertFalse(self.event.is_closed)

    def test_student_can_join_and_publish_and_comment_in_active_event(self):
        self.client.force_login(self.student)
        self.client.post(reverse("join_event", args=[self.event.pk]))
        response = self.client.post(
            reverse("create_event_post", args=[self.event.pk]),
            {"title": "Having a great time", "body": "The event is fun."},
        )

        post = Post.objects.get(event=self.event)
        self.assertRedirects(
            response,
            reverse("event_detail", args=[self.event.pk]),
        )
        self.assertTrue(self.event.is_member(self.student))
        self.assertEqual(post.author, self.student)

        response = self.client.post(
            reverse("create_comment", args=[post.pk]),
            {"body": "Glad you are enjoying it!"},
        )
        comment = Comment.objects.get(post=post)
        self.assertRedirects(
            response,
            reverse("event_detail", args=[self.event.pk]),
        )
        self.assertEqual(comment.author, self.student)

    def test_student_must_join_before_posting(self):
        self.client.force_login(self.student)
        self.client.post(
            reverse("create_event_post", args=[self.event.pk]),
            {"title": "Unjoined post", "body": "Not allowed."},
        )

        self.assertFalse(Post.objects.filter(event=self.event).exists())

    def test_admin_can_close_event_and_no_new_discussion_is_allowed(self):
        self.client.force_login(self.student)
        self.event.members.add(self.student)
        post = Post.objects.create(
            author=self.student,
            event=self.event,
            title="Event post",
            body="Discussion.",
        )
        self.client.force_login(self.staff)
        response = self.client.post(reverse("close_event", args=[self.event.pk]))

        self.event.refresh_from_db()
        self.assertRedirects(response, reverse("event_detail", args=[self.event.pk]))
        self.assertTrue(self.event.is_closed)
        self.assertFalse(self.event.can_join)
        self.assertFalse(self.event.can_discuss)

        self.client.force_login(self.student)
        self.client.post(
            reverse("create_comment", args=[post.pk]),
            {"body": "A late comment."},
        )
        self.assertFalse(Comment.objects.filter(post=post).exists())

    def test_event_end_time_automatically_closes_discussion_and_joining(self):
        self.event.ends_at = timezone.now() - timedelta(minutes=1)
        self.event.save(update_fields=["ends_at"])

        self.assertFalse(self.event.can_join)
        self.assertFalse(self.event.can_discuss)
        self.client.force_login(self.student)
        self.client.post(
            reverse("join_event", args=[self.event.pk]),
        )
        self.client.post(
            reverse("create_event_post", args=[self.event.pk]),
            {"title": "Late post", "body": "Not allowed."},
        )
        self.assertFalse(self.event.is_member(self.student))
        self.assertFalse(Post.objects.filter(event=self.event).exists())
