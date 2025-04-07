from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Deletes unverified user accounts that are older than 2 minutes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=2,
            help='Number of minutes after which unverified accounts should be deleted',
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        
        # Get all unverified accounts created before the cutoff
        unverified_users = User.objects.filter(
            email_is_verified=False,
            verification_token_created__lt=cutoff_time,
        )
        
        count = unverified_users.count()
        if count:
            self.stdout.write(self.style.WARNING(f'Found {count} unverified accounts older than {minutes} minutes'))
            
            # List accounts that will be deleted
            for user in unverified_users:
                created_at = user.verification_token_created
                time_diff = timezone.now() - created_at if created_at else None
                self.stdout.write(f'  - {user.email} (created: {created_at}, age: {time_diff})')
            
            # Delete the accounts
            unverified_users.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} unverified accounts'))
        else:
            self.stdout.write(self.style.SUCCESS('No unverified accounts to delete'))