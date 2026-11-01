"""
URL configuration for campus_connect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth.views import PasswordResetView
from django.conf import settings
from django.urls import path, include

from community.views import(
    create_comment,
    create_event,
    create_event_post,
    create_group_post,
    create_post,
    bookmarks,
    about,
    group_detail,
    group_list,
    event_detail,
    event_list,
    home,
    join_event,
    close_event,
    join_group,
    leave_group,
    remove_comment,
    remove_post,
    signup,
    toggle_post_pin,
    toggle_post_bookmark,

)


class ConfiguredPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        self.extra_email_context = {
            **(self.extra_email_context or {}),
            "password_reset_base_url": settings.PASSWORD_RESET_BASE_URL,
        }
        return super().form_valid(form)


"""

urls.py was editted by randy

variables added
-accounts/
-accounts/singup/
-home/

"""



urlpatterns = [
    path("", home, name="home"),
    path("about/", about, name="about"),

    path("posts/create/", create_post, name="create_post"),
    path("posts/<int:post_id>/comments/create/", create_comment, name="create_comment"),
    path("posts/<int:post_id>/bookmark/", toggle_post_bookmark, name="toggle_post_bookmark"),
    path("bookmarks/", bookmarks, name="bookmarks"),

    path("post/<int:post_id>/remove", remove_post, name="remove_post"),
    path("comments/<int:comment_id>/remove/", remove_comment, name="remove_comment"),


    # groups
    path("groups/", group_list, name="group_list"),
    path("groups/<slug:slug>/", group_detail, name="group_detail"),
    path("groups/<slug:slug>/join/", join_group, name="join_group"),
    path("groups/<slug:slug>/leave/", leave_group, name="leave_group"),
    path("groups/<slug:slug>/posts/create/", create_group_post, name="create_group_post"),

    # Events
    path("events/", event_list, name="event_list"),
    path("events/create/", create_event, name="create_event"),
    path("events/<int:event_id>/", event_detail, name="event_detail"),
    path("events/<int:event_id>/join/", join_event, name="join_event"),
    path("events/<int:event_id>/posts/create/", create_event_post, name="create_event_post"),
    path("events/<int:event_id>/close/", close_event, name="close_event"),

    path("admin/", admin.site.urls),
    path(
        "accounts/password_reset/",
        ConfiguredPasswordResetView.as_view(),
        name="password_reset",
    ),
    path("accounts/", include("django.contrib.auth.urls")),

    path("posts/<int:post_id>/pin/", toggle_post_pin, name="toggle_post_pin"),
    
    
    path("accounts/signup/", signup, name="signup"),
]
