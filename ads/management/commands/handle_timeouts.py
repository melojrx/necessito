"""
Management command to handle state machine timeouts automatically.
This command should be run periodically (e.g., via cron or celery beat).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from ads.models import Necessidade
from core.state_machine import StateTransitionError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Handle state machine timeouts for Necessidade objects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        """Handle timeout processing for necessidades."""
        dry_run = options['dry_run']
        verbose = options['verbose']

        if dry_run:
            self.stdout.write(
                self.style.WARNING('Running in DRY RUN mode - no changes will be made')
            )

        # Find necessidades in aguardando_confirmacao status that might have expired
        expired_necessidades = Necessidade.objects.filter(
            status='aguardando_confirmacao',
            aguardando_confirmacao_desde__isnull=False,
            aguardando_confirmacao_desde__lt=timezone.now() - timedelta(hours=48)
        )

        total_processed = 0
        total_errors = 0

        for necessidade in expired_necessidades:
            try:
                if verbose:
                    self.stdout.write(
                        f'Processing necessidade {necessidade.id}: {necessidade.titulo}'
                    )

                # Check if timeout handling is needed
                if necessidade.is_confirmation_expired():
                    if not dry_run:
                        # Handle the timeout
                        success = necessidade.handle_timeout()
                        if success:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Successfully handled timeout for necessidade {necessidade.id}'
                                )
                            )
                            total_processed += 1
                        else:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'Failed to handle timeout for necessidade {necessidade.id}'
                                )
                            )
                            total_errors += 1
                    else:
                        self.stdout.write(
                            f'Would handle timeout for necessidade {necessidade.id}'
                        )
                        total_processed += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing necessidade {necessidade.id}: {str(e)}'
                    )
                )
                total_errors += 1
                logger.error(f'Error in timeout handler for necessidade {necessidade.id}: {str(e)}')

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'  Processed: {total_processed}\n'
                f'  Errors: {total_errors}\n'
                f'  Total checked: {expired_necessidades.count()}'
            )
        )

        # Also check for other timeout scenarios if needed
        self._check_other_timeouts(dry_run, verbose)

    def _check_other_timeouts(self, dry_run, verbose):
        """Check for other timeout scenarios that might need handling."""
        
        # Example: Check for very old 'ativo' necessidades that should be expired
        old_active = Necessidade.objects.filter(
            status='ativo',
            data_criacao__lt=timezone.now() - timedelta(days=30)  # 30 days old
        )

        if old_active.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\nFound {old_active.count()} old active necessidades (>30 days). '
                    'Consider implementing expiration logic for these.'
                )
            )

        # Example: Check for necessidades stuck in analisando_orcamentos for too long
        stuck_analyzing = Necessidade.objects.filter(
            status='analisando_orcamentos',
            data_primeiro_orcamento__lt=timezone.now() - timedelta(days=15)  # 15 days analyzing
        )

        if stuck_analyzing.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Found {stuck_analyzing.count()} necessidades stuck in analysis for >15 days. '
                    'Consider implementing cleanup logic.'
                )
            )