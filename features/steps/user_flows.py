from behave import given, then, when


@given("I open the account creation page")
def open_signup_page(context):
    from django.urls import reverse

    context.response = context.client.get(reverse("signup"))


@when("I submit these account details:")
def submit_account_details(context):
    from django.urls import reverse

    context.response = context.client.post(
        reverse("signup"),
        dict(context.table[0].items()),
    )


@then("I am redirected to the home page")
def check_home_redirect(context):
    from django.urls import reverse

    assert context.response.status_code == 302
    assert context.response["Location"] == reverse("home")


@then('an account exists for "{username}"')
def check_account_exists(context, username):
    from django.contrib.auth.models import User

    assert User.objects.filter(username=username).exists()

@then("signup is rejected and the existing account is unchanged")
def check_duplicate_signup_rejected(context):
    from django.contrib.auth import get_user_model

    assert context.response.status_code == 200
    assert get_user_model().objects.filter(username="existinguser").count() == 1



@then('I am logged in as "{username}"')
def check_authenticated_user(context, username):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.get(username=username)
    assert str(context.client.session.get("_auth_user_id")) == str(user.pk)


@given('I am logged in as "{username}"')
def login_user(context, username):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.get(username=username)
    context.client.force_login(user)
    context.current_user = user
    assert str(context.client.session["_auth_user_id"]) == str(user.pk)


@given('a registered user "{username}" exists')
def create_registered_user(context, username):
    from django.contrib.auth import get_user_model

    get_user_model().objects.create_user(
        username=username,
        password="Campus-connect-2026!",
    )


@when('I publish a post titled "{title}" with body "{body}"')
def publish_post(context, title, body):
    from django.urls import reverse

    context.post_title = title
    context.response = context.client.post(
        reverse("create_post"),
        {"title": title, "body": body},
    )


@then('the post "{title}" appears on the home page')
def check_post_on_home(context, title):
    from django.urls import reverse

    response = context.client.get(reverse("home"))
    assert response.status_code == 200
    assert title in [post.title for post in response.context["posts"]]


@then('the post was written by "{username}"')
def check_post_author(context, username):
    from community.models import Post

    post = Post.objects.get(title=context.post_title)
    assert post.author.username == username


@then("I am redirected to the login page")
def check_login_redirect(context):
    from django.urls import reverse

    assert context.response.status_code == 302
    assert context.response["Location"].startswith(reverse("login"))


@then('no post titled "{title}" exists')
def check_post_does_not_exist(context, title):
    from community.models import Post

    assert not Post.objects.filter(title=title).exists()

@given('a group "{name}" with slug "{slug}" exists')
def create_group(context, name, slug):
    from community.models import Group

    Group.objects.create(name=name, slug=slug)


@when('I join the group "{slug}"')
def join_group(context, slug):
    from django.urls import reverse

    context.response = context.client.post(reverse("join_group", args=[slug]))


@then('I am a member of the group "{slug}"')
def check_group_membership(context, slug):
    from community.models import Group

    group = Group.objects.get(slug=slug)
    assert group.members.filter(pk=context.current_user.pk).exists()


@given('the user is already a member of the group "{slug}"')
def add_user_to_group(context, slug):
    from community.models import Group

    group = Group.objects.get(slug=slug)
    group.members.add(context.current_user)


@when(
    'I publish a group post titled "{title}" with body "{body}" in "{slug}"'
)
def publish_group_post(context, title, body, slug):
    from django.urls import reverse

    context.post_title = title
    context.response = context.client.post(
        reverse("create_group_post", args=[slug]),
        {"title": title, "body": body},
    )


@then('the post "{title}" exists in the group "{slug}"')
def check_group_post(context, title, slug):
    from community.models import Group, Post

    group = Group.objects.get(slug=slug)
    assert Post.objects.filter(title=title, group=group).exists()


@given('a post titled "{title}" by "{username}" exists')
def create_post_for_bookmarking(context, title, username):
    from django.contrib.auth import get_user_model
    from community.models import Post

    author = get_user_model().objects.get(username=username)
    Post.objects.create(author=author, title=title, body="Post body")


@when('I bookmark the post titled "{title}"')
def toggle_post_bookmark(context, title):
    from django.urls import reverse
    from community.models import Post

    post = Post.objects.get(title=title)
    context.response = context.client.post(
        reverse("toggle_post_bookmark", args=[post.pk])
    )


@then('the post "{title}" appears in my bookmarks')
def check_post_is_bookmarked(context, title):
    from django.urls import reverse
    from community.models import Post

    post = Post.objects.get(title=title)
    assert post.bookmarked_by.filter(pk=context.current_user.pk).exists()
    response = context.client.get(reverse("bookmarks"))
    assert response.status_code == 200
    assert title in response.content.decode()


@then('the post "{title}" is not in my bookmarks')
def check_post_is_not_bookmarked(context, title):
    from community.models import Post

    post = Post.objects.get(title=title)
    assert not post.bookmarked_by.filter(pk=context.current_user.pk).exists()
