"""
Management command to set up PyLadies Seoul homepage.
This ensures the homepage is properly configured regardless of deployment method.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import Site, Page
from apps.content.models import HomePage


class Command(BaseCommand):
    help = 'Set up PyLadies Seoul homepage and site configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of homepage even if it exists',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            try:
                self.setup_homepage(force=options['force'])
                self.stdout.write(
                    self.style.SUCCESS('Successfully set up PyLadies Seoul homepage!')
                )
            except Exception as e:
                raise CommandError(f'Failed to set up homepage: {e}')

    def setup_homepage(self, force=False):
        """Set up the homepage and site configuration"""
        
        # Check if HomePage already exists
        existing_home = HomePage.objects.first()
        if existing_home and not force:
            self.stdout.write(f'Homepage already exists: {existing_home.title}')
            self.ensure_site_configuration(existing_home)
            return existing_home

        # Remove default Wagtail welcome page if it exists
        welcome_page = Page.objects.filter(
            slug='home',
            depth=2
        ).exclude(
            content_type__model='homepage'
        ).first()
        
        if welcome_page:
            self.stdout.write(f'Removing default welcome page: {welcome_page.title}')
            welcome_page.delete()

        # Remove existing HomePage if force is specified
        if force and existing_home:
            self.stdout.write(f'Removing existing homepage: {existing_home.title}')
            existing_home.delete()

        # Get root page
        root_page = Page.objects.get(depth=1)
        
        # Create PyLadies Seoul homepage
        self.stdout.write('Creating PyLadies Seoul homepage...')
        
        home_page = HomePage.objects.create(
            title='PyLadies Seoul',
            hero_title='PyLadies Seoul',
            hero_subtitle='<p>파이썬을 사랑하는 여성 개발자 커뮤니티</p>',
            hero_cta_text='Join Us',
            hero_cta_url='https://pyladiesseoul.org/contact/',
            slug='home',
            path=root_page.path + '0001',
            depth=2,
            numchild=0,
            live=True,
            has_unpublished_changes=False
        )
        
        # Create and publish initial revision
        revision = home_page.save_revision()
        revision.publish()
        
        self.stdout.write(f'Created homepage: {home_page.title} ({home_page.url})')
        
        # Ensure site configuration
        self.ensure_site_configuration(home_page)
        
        return home_page

    def ensure_site_configuration(self, home_page):
        """Ensure site is properly configured with the homepage"""
        
        # Get or create default site
        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'hostname': 'localhost',
                'site_name': 'PyLadies Seoul',
                'root_page': home_page,
                'port': 8000
            }
        )
        
        # Update site if it exists but doesn't point to our homepage
        if not created and site.root_page != home_page:
            site.root_page = home_page
            site.site_name = 'PyLadies Seoul'
            site.save()
            self.stdout.write(f'Updated site configuration: {site.site_name}')
        elif created:
            self.stdout.write(f'Created site configuration: {site.site_name}')
        else:
            self.stdout.write(f'Site configuration is already correct: {site.site_name}')