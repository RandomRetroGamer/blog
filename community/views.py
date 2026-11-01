
"""
Views.py created by Randy Coronado

functions created
- signup(request)
- home(request)



"""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import BooleanField, Exists, OuterRef, Value
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .authority_forms import SignupForm
from .forms import CommentForm, EventForm, PostForm
from .models import Comment, Event, Group, Post


def _posts_with_bookmark_state(posts, user):
    if user.is_authenticated:
        bookmarks = Post.bookmarked_by.through.objects.filter(
            post_id=OuterRef("pk"),
            user_id=user.pk,
        )
        event_memberships = Event.members.through.objects.filter(
            event_id=OuterRef("event_id"),
            user_id=user.pk,
        )
        return posts.annotate(
            is_bookmarked=Exists(bookmarks),
            is_event_member=Exists(event_memberships),
        )
    return posts.annotate(
        is_bookmarked=Value(False, output_field=BooleanField()),
        is_event_member=Value(False, output_field=BooleanField()),
    )


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {
        "form": form,
    })


"""
a stupidly simple function to get base.html running as soon we start it
"""

@never_cache
def home(request):
    return render(request, "base.html", {
        "posts": _posts_with_bookmark_state(
            Post.objects.select_related("author", "group").prefetch_related(
                "comments__author"
            ),
            request.user,
        ),
        "post_form": PostForm(),
        "comment_form": CommentForm(),
    })


def about(request):
    return render(request, "community/about.html")


@login_required
def bookmarks(request):
    posts = request.user.bookmarked_posts.select_related(
        "author", "group"
    ).prefetch_related("comments__author")
    return render(request, "community/bookmarks.html", {
        "posts": _posts_with_bookmark_state(posts, request.user),
        "comment_form": CommentForm(),
    })


@login_required
@require_POST
def toggle_post_bookmark(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.bookmarked_by.filter(pk=request.user.pk).exists():
        post.bookmarked_by.remove(request.user)
        messages.success(request, "Post removed from your bookmarks.")
    else:
        post.bookmarked_by.add(request.user)
        messages.success(request, "Post added to your bookmarks.")

    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    if post.group:
        return redirect("group_detail", slug=post.group.slug)
    return redirect("home")


def csrf_failure(request, reason=""):
    return render(request, "403_csrf.html", status=403)

@login_required
def create_post(request):
    if request.method != "POST":
        return redirect("home")

    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Your post was published.")
    else:
        messages.error(request, "; ".join(
            error for errors in form.errors.values() for error in errors
        ))
    return redirect("home")


@login_required
def create_comment(request, post_id):
    if request.method != "POST":
        return redirect("home")

    post = get_object_or_404(Post, pk=post_id)
    if post.event and (
        not post.event.can_discuss
        or not post.event.is_member(request.user)
    ):
        messages.error(request, "Join an active event before commenting.")
        if post.event:
            return redirect("event_detail", event_id=post.event_id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, "Your comment was added.")
    else:
        messages.error(request, "; ".join(
            error for errors in form.errors.values() for error in errors
        ))

    # send the user back to the group page if the post is in a group
    if post.group:
        return redirect("group_detail", slug=post.group.slug)
    if post.event:
        return redirect("event_detail", event_id=post.event_id)
    return redirect("home")

@staff_member_required(login_url="login")
@require_POST
def remove_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    messages.success(request, " The Post and Its comment were removed. ")
    return redirect("home")

"""
the first step so admins can pin a post to the top of the page

"""


@staff_member_required(login_url="login")
@require_POST
def toggle_post_pin(request, post_id):
    
    post = get_object_or_404(Post, pk=post_id)
    post.is_pinned = not post.is_pinned
    post.save(update_fields=["is_pinned"])

    action = "pinned" if post.is_pinned else "unpinned"
    messages.success(request, f'The post "{post.title}" was {action}.')

    if post.group:
        return redirect("group_detail", slug=post.group.slug)
    return redirect("home")



@staff_member_required(login_url="login")
@require_POST

def remove_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    messages.success(request, " the comment was removed ")
    return redirect("home")


"""
Group views

- group_list(request)          shows every group
- group_detail(request, slug)  shows one group and its posts
- join_group / leave_group     adds or removes the user from a group
- create_group_post            makes a post inside a group (members only)
"""

def group_list(request):
    groups = Group.objects.all().order_by("name")

    print("GROUP LIST DEBUG")
    print("Database vendor:", Group.objects.db)
    print("Total groups:", groups.count())
    print("Group names:", list(groups.values_list("name", flat=True)))

    my_groups = []
    if request.user.is_authenticated:
        my_groups = list(
            request.user.community_groups.values_list("pk", flat=True)
        )

    return render(request, "community/group_list.html", {
        "groups": groups,
        "my_groups": my_groups,
    })


@never_cache
def group_detail(request, slug):
    group = get_object_or_404(Group, slug=slug)

    return render(request, "community/group_detail.html", {
        "group": group,
        "is_member": group.is_member(request.user),
        "posts": _posts_with_bookmark_state(
            group.posts.select_related("author").prefetch_related(
                "comments__author"
            ),
            request.user,
        ),
        "post_form": PostForm(),
        "comment_form": CommentForm(),
    })


@login_required
@require_POST
def join_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group.members.add(request.user)
    messages.success(request, f"You joined {group.name}.")
    return redirect("group_detail", slug=group.slug)


@login_required
@require_POST
def leave_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group.members.remove(request.user)
    messages.success(request, f"You left {group.name}.")
    return redirect("group_detail", slug=group.slug)


@login_required
@require_POST
def create_group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)

    # only members can post in a group
    if not group.is_member(request.user):
        messages.error(request, f"Join {group.name} before posting in it.")
        return redirect("group_detail", slug=group.slug)

    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.group = group
        post.save()
        messages.success(request, "Your post was published.")
    else:
        messages.error(request, "; ".join(
            error for errors in form.errors.values() for error in errors
        ))
    return redirect("group_detail", slug=group.slug)


def event_list(request):
    return render(request, "community/event_list.html", {
        "events": Event.objects.prefetch_related("members"),
    })


@never_cache
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_member = event.is_member(request.user)
    return render(request, "community/event_detail.html", {
        "event": event,
        "is_member": is_member,
        "posts": _posts_with_bookmark_state(
            event.posts.select_related("author", "event").prefetch_related(
                "comments__author"
            ),
            request.user,
        ),
        "post_form": PostForm(),
        "comment_form": CommentForm(),
    })


@login_required
@require_POST
def join_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not event.can_join:
        messages.error(request, "This event is closed to new participants.")
    else:
        event.members.add(request.user)
        messages.success(request, f"You joined {event.title}.")
    return redirect("event_detail", event_id=event.pk)


@login_required
@require_POST
def create_event_post(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not event.is_member(request.user):
        messages.error(request, f"Join {event.title} before posting.")
        return redirect("event_detail", event_id=event.pk)
    if not event.can_discuss:
        messages.error(request, "Event discussions are not currently open.")
        return redirect("event_detail", event_id=event.pk)

    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.event = event
        post.save()
        messages.success(request, "Your event post was published.")
    else:
        messages.error(request, "; ".join(
            error for errors in form.errors.values() for error in errors
        ))
    return redirect("event_detail", event_id=event.pk)


@staff_member_required(login_url="login")
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f"{event.title} was created.")
            return redirect("event_detail", event_id=event.pk)
    else:
        form = EventForm()
    return render(request, "community/event_form.html", {"form": form})


@staff_member_required(login_url="login")
@require_POST
def close_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not event.is_closed:
        event.is_closed = True
        event.save(update_fields=["is_closed"])
        messages.success(request, f"{event.title} has been closed.")
    return redirect("event_detail", event_id=event.pk)
