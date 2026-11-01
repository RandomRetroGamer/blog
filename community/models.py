"""
models.py was editted to add posting functions to the project
- changes made by randy coronado

This is the very start where the users can post / comment
on the home.html

file edited by randy coronado 10/19/2026

"""
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Group(models.Model):
    """
    A group students can join, like Computer Science or Engineering.
    Members of a group can post inside of it.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(
        User,
        related_name="community_groups",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def is_member(self, user):
        return user.is_authenticated and self.members.filter(pk=user.pk).exists()


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_community_events",
    )
    members = models.ManyToManyField(
        User,
        related_name="community_events",
        blank=True,
    )
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at", "title"]

    def __str__(self):
        return self.title

    def is_member(self, user):
        return user.is_authenticated and self.members.filter(pk=user.pk).exists()

    @property
    def can_join(self):
        return not self.is_closed and timezone.now() < self.ends_at

    @property
    def is_upcoming(self):
        now = timezone.now()
        return not self.is_closed and now < self.starts_at < self.ends_at

    @property
    def can_discuss(self):
        now = timezone.now()
        return not self.is_closed and self.starts_at <= now < self.ends_at


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="community_posts",
    )
    # posts made before groups existed don't have a group, so this can be empty
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="posts",
        null=True,
        blank=True,
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="posts",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=200)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)

    bookmarked_by = models.ManyToManyField(
        User,
        related_name="bookmarked_posts",
        blank=True,
    )

    bookmarked_by = models.ManyToManyField(
        User,
        related_name="bookmarked_posts",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="community_comments",
    )
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
