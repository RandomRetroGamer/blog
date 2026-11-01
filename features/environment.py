import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_connect.settings")

import django

django.setup()


def before_all(context):
    from django.conf import settings
    from django.test import override_settings
    from django.test.runner import DiscoverRunner

    context.allowed_hosts_override = override_settings(
        ALLOWED_HOSTS=["testserver", *settings.ALLOWED_HOSTS]
    )
    context.allowed_hosts_override.enable()
    context.test_runner = DiscoverRunner(verbosity=0, interactive=False)
    context.test_runner.setup_test_environment()
    context.database_config = context.test_runner.setup_databases()


def before_scenario(context, scenario):
    from django.core.management import call_command
    from django.test import Client

    call_command("flush", interactive=False, verbosity=0)
    context.client = Client()
    context.response = None


def after_all(context):
    if hasattr(context, "database_config"):
        context.test_runner.teardown_databases(context.database_config)
        context.test_runner.teardown_test_environment()
    if hasattr(context, "allowed_hosts_override"):
        context.allowed_hosts_override.disable()
