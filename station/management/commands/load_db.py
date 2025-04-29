import time

from django.core.management import BaseCommand
from django.db import connections, OperationalError


class Command(BaseCommand):
    def handle(self, *args, **options):
        db = connections['default']
        connected = False

        while not connected:
            try:
                db.ensure_connection()
                connected = True
                self.stdout.write('Connected to database successfully.')
            except OperationalError:
                self.stdout.write('Database connection failed.')
                time.sleep(1)
