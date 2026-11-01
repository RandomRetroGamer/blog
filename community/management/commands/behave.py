import argparse

from behave.__main__ import main as behave_main
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Run the project's Behave feature tests."

    def add_arguments(self, parser):
        parser.add_argument(
            "behave_args",
            nargs=argparse.REMAINDER,
            help="Optional arguments to pass to Behave.",
        )

    def handle(self, *args, **options):
        result = behave_main(args=["features", *options["behave_args"]])
        if result:
            raise CommandError("Behave feature tests failed.")