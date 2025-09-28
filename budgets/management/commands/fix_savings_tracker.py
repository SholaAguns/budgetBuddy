from django.core.management.base import BaseCommand
from budgets.models import SavingsTracker
from budgets.services.savings_service import SavingsService


class Command(BaseCommand):
    help = 'Fix and update all savings tracker projections'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-categories',
            action='store_true',
            help='Create required savings categories if they don\'t exist',
        )

    def handle(self, *args, **options):
        savings_service = SavingsService()

        if options['create_categories']:
            self.stdout.write('Creating required savings categories...')
            created = savings_service.ensure_savings_categories_exist()
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created categories: {", ".join(created)}')
                )
            else:
                self.stdout.write('All required categories already exist.')

        self.stdout.write('Updating all savings tracker projections...')

        trackers = SavingsTracker.objects.all()
        updated_count = 0

        for tracker in trackers:
            try:
                savings_service.update_savings(tracker)
                updated_count += 1
                self.stdout.write(f'Updated tracker for user: {tracker.user.username}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error updating tracker for {tracker.user.username}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} savings trackers.')
        )