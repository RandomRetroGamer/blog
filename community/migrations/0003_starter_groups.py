"""
Creates the first groups so the site isn't empty when someone sets it up.
Admins can add more groups from /admin/.
"""
from django.db import migrations

STARTER_GROUPS = [
    ("Computer Science", "computer-science", "Coding help, CS classes, and hackathons."),
    ("Engineering", "engineering", "Engineering classes, projects, and study groups."),
]


def add_groups(apps, schema_editor):
    Group = apps.get_model("community", "Group")
    for name, slug, description in STARTER_GROUPS:
        Group.objects.get_or_create(
            slug=slug, defaults={"name": name, "description": description}
        )


def remove_groups(apps, schema_editor):
    Group = apps.get_model("community", "Group")
    Group.objects.filter(slug__in=[slug for _, slug, _ in STARTER_GROUPS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0002_groups"),
    ]

    operations = [
        migrations.RunPython(add_groups, remove_groups),
    ]
