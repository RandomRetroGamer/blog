"""
test created so far

- for login / signup - Created by Randy Coronado
[10/17/2026]

- for post / comment - Created by Randy Coronado

- for groups


"""
from django.contrib.auth.models import User
from django.conf import settings

from django.urls import reverse

from .models import Comment, Group, Post
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


from .authority_forms import SignupForm


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="Old-password-2026!",
        )

    def test_login_page_has_password_reset_link(self):
        response = self.client.get(reverse("login"))

        self.assertContains(response, reverse("password_reset"))

    @override_settings(PASSWORD_RESET_BASE_URL="https://campusconnect.example.test")
    def test_password_reset_sends_email(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": self.user.email},
            HTTP_HOST="localhost:8000",
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("resetuser@example.com", mail.outbox[0].to)
        self.assertIn(
            f"{settings.PASSWORD_RESET_BASE_URL}/accounts/reset/",
            mail.outbox[0].body,
        )
        self.assertNotIn("http://localhost:8000/accounts/reset/", mail.outbox[0].body)

    def test_password_reset_updates_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        confirm_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})

        response = self.client.get(confirm_url, follow=True)
        reset_url = response.redirect_chain[-1][0]
        response = self.client.post(
            reset_url,
            {
                "new_password1": "New-password-2026!",
                "new_password2": "New-password-2026!",
            },
        )

        self.assertRedirects(response, reverse("password_reset_complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-password-2026!"))
        self.assertFalse(self.user.check_password("Old-password-2026!"))

    def test_invalid_password_reset_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        confirm_url = reverse(
            "password_reset_confirm",
            kwargs={"uidb64": uid, "token": "invalid-token"},
        )

        response = self.client.get(confirm_url)

        self.assertContains(response, "Reset link unavailable")


class SignupTests(TestCase):
    def test_valid_signup_redirects_to_home_and_logs_user_in(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "Campus-connect-test-2026!",
                "password2": "Campus-connect-test-2026!",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(User.objects.filter(username="newuser").exists())


class PostAndCommentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="test-password",
        )

    def test_authenticated_user_can_create_post(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("create_post"),
            {"title": "Campus event", "body": "Let's meet this Friday."},
        )

        self.assertRedirects(response, reverse("home"))
        post = Post.objects.get()
        self.assertEqual(post.title, "Campus event")
        self.assertEqual(post.body, "Let's meet this Friday.")
        self.assertEqual(post.author, self.user)

    def test_anonymous_user_cannot_create_post(self):
        response = self.client.post(
            reverse("create_post"),
            {"title": "Campus event", "body": "Let's meet this Friday."},
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('create_post')}",
        )
        self.assertFalse(Post.objects.exists())

    def test_authenticated_user_can_comment_on_post(self):
        post = Post.objects.create(
            author=self.user,
            title="Campus event",
            body="Let's meet this Friday.",
        )
        commenter = User.objects.create_user(
            username="commenter",
            password="test-password",
        )
        self.client.force_login(commenter)

        response = self.client.post(
            reverse("create_comment", args=[post.pk]),
            {"body": "Sounds good!"},
        )

        self.assertRedirects(response, reverse("home"))
        comment = Comment.objects.get()
        self.assertEqual(comment.body, "Sounds good!")
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.author, commenter)

    def test_anonymous_user_cannot_comment_on_post(self):
        post = Post.objects.create(
            author=self.user,
            title="Campus event",
            body="Let's meet this Friday.",
        )

        response = self.client.post(
            reverse("create_comment", args=[post.pk]),
            {"body": "Sounds good!"},
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('create_comment', args=[post.pk])}",
        )
        self.assertFalse(Comment.objects.exists())


class ModerationTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="postauthor",
            password="test-password",
        )
        self.staff_user = User.objects.create_user(
            username="moderator",
            password="test-password",
            is_staff=True,
        )
        self.post = Post.objects.create(
            author=self.author,
            title="Campus event",
            body="Let's meet this Friday.",
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            body="Sounds good!",
        )

    def test_staff_can_remove_post_and_its_comments(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("remove_post", args=[self.post.pk]),
        )

        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_staff_can_remove_comment(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("remove_comment", args=[self.comment.pk]),
        )

        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_non_staff_cannot_remove_post_or_comment(self):
        self.client.force_login(self.author)

        post_response = self.client.post(
            reverse("remove_post", args=[self.post.pk]),
        )
        comment_response = self.client.post(
            reverse("remove_comment", args=[self.comment.pk]),
        )

        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(comment_response.status_code, 302)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_staff_moderation_actions_require_post(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse("remove_comment", args=[self.comment.pk]),
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_stale_csrf_token_shows_recovery_instructions_without_removing_post(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff_user)
        feed_response = client.get(reverse("home"))
        old_token = client.cookies["csrftoken"].value

        client.cookies["csrftoken"] = "rotated-token"
        response = client.post(
            reverse("remove_post", args=[self.post.pk]),
            {"csrfmiddlewaretoken": old_token},
        )

        self.assertEqual(feed_response.status_code, 200)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "refresh it, and try again", status_code=403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_feed_is_not_cached_with_csrf_tokens(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("home"))

        self.assertIn("no-store", response["Cache-Control"])


class GroupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            password="test-password",
        )
        self.group = Group.objects.create(
            name="Test Group",
            slug="test-group",
            description="A group for testing.",
        )

    def test_starter_groups_exist(self):
        self.assertTrue(Group.objects.filter(slug="computer-science").exists())
        self.assertTrue(Group.objects.filter(slug="engineering").exists())

    def test_group_list_page_shows_groups(self):
        response = self.client.get(reverse("group_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Group")

    def test_user_can_join_and_leave_group(self):
        self.client.force_login(self.user)

        self.client.post(reverse("join_group", args=[self.group.slug]))
        self.assertTrue(self.group.is_member(self.user))

        self.client.post(reverse("leave_group", args=[self.group.slug]))
        self.assertFalse(self.group.is_member(self.user))

    def test_anonymous_user_cannot_join_group(self):
        response = self.client.post(reverse("join_group", args=[self.group.slug]))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('join_group', args=[self.group.slug])}",
        )
        self.assertEqual(self.group.members.count(), 0)

    def test_member_can_post_in_group(self):
        self.group.members.add(self.user)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("create_group_post", args=[self.group.slug]),
            {"title": "Study session", "body": "Library at 5?"},
        )

        self.assertRedirects(response, reverse("group_detail", args=[self.group.slug]))
        post = Post.objects.get()
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)

    def test_non_member_cannot_post_in_group(self):
        self.client.force_login(self.user)

        self.client.post(
            reverse("create_group_post", args=[self.group.slug]),
            {"title": "Study session", "body": "Library at 5?"},
        )

        self.assertFalse(Post.objects.exists())

    def test_group_page_only_shows_its_own_posts(self):
        other_group = Group.objects.create(name="Other Group", slug="other-group")
        Post.objects.create(author=self.user, group=self.group, title="In this group", body="hi")
        Post.objects.create(author=self.user, group=other_group, title="In other group", body="hi")

        response = self.client.get(reverse("group_detail", args=[self.group.slug]))

        self.assertContains(response, "In this group")
        self.assertNotContains(response, "In other group")

class BookmarkTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bookmarkuser",
            password="Campus-connect-test-2026!",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="Campus-connect-test-2026!",
        )
        self.post = Post.objects.create(
            author=self.other_user,
            title="Important campus update",
            body="Please remember this update.",
        )

    def test_user_can_bookmark_and_remove_a_post(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("toggle_post_bookmark", args=[self.post.pk]),
            {"next": reverse("home")},
        )

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(self.post.bookmarked_by.filter(pk=self.user.pk).exists())

        response = self.client.post(
            reverse("toggle_post_bookmark", args=[self.post.pk]),
            {"next": reverse("home")},
        )

        self.assertRedirects(response, reverse("home"))
        self.assertFalse(self.post.bookmarked_by.filter(pk=self.user.pk).exists())

    def test_bookmarks_are_private_and_listed_on_bookmarks_page(self):
        self.post.bookmarked_by.add(self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("bookmarks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Important campus update")
        self.assertContains(response, "Remove bookmark")

        self.client.force_login(self.other_user)
        response = self.client.get(reverse("bookmarks"))
        self.assertNotContains(response, "Important campus update")

    def test_feed_shows_bookmark_state_only_to_the_current_user(self):
        self.post.bookmarked_by.add(self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("home"))
        self.assertContains(response, "Remove bookmark")

        self.client.force_login(self.other_user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Bookmark as important")
        self.assertNotContains(response, "Remove bookmark")

    def test_anonymous_user_cannot_bookmark_or_view_bookmarks(self):
        bookmark_response = self.client.post(
            reverse("toggle_post_bookmark", args=[self.post.pk]),
        )
        bookmarks_response = self.client.get(reverse("bookmarks"))

        self.assertRedirects(
            bookmark_response,
            f"{reverse('login')}?next={reverse('toggle_post_bookmark', args=[self.post.pk])}",
        )
        self.assertRedirects(
            bookmarks_response,
            f"{reverse('login')}?next={reverse('bookmarks')}",
        )
        self.assertFalse(self.post.bookmarked_by.exists())

    def test_bookmark_toggle_requires_post_and_rejects_external_redirect(self):
        self.client.force_login(self.user)

        get_response = self.client.get(
            reverse("toggle_post_bookmark", args=[self.post.pk]),
        )
        response = self.client.post(
            reverse("toggle_post_bookmark", args=[self.post.pk]),
            {"next": "https://example.com/"},
        )

        self.assertEqual(get_response.status_code, 405)
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(self.post.bookmarked_by.filter(pk=self.user.pk).exists())
