"""
Management command to create initial contribute methods data
"""

from django.core.management.base import BaseCommand
from apps.content.models import ContributeMethod


class Command(BaseCommand):
    help = 'Create initial contribute methods for Connect page'

    def handle(self, *args, **options):
        contribute_methods = [
            {
                'title': '기부',
                'description': 'PyLadies Seoul의 활동을 지원해주세요. 여러분의 후원이 더 많은 여성 개발자들에게 기회를 제공합니다.',
                'icon_class': 'fas fa-heart',
                'link_url': '',
                'link_text': '자세히 보기',
                'order': 1,
                'is_active': True,
            },
            {
                'title': '자원봉사',
                'description': '이벤트 기획, 운영, 홍보 등 다양한 방법으로 PyLadies Seoul과 함께해주세요.',
                'icon_class': 'fas fa-hands-helping',
                'link_url': '',
                'link_text': '자세히 보기',
                'order': 2,
                'is_active': True,
            },
            {
                'title': '연사자 지원',
                'description': '여러분의 경험과 지식을 공유하고 다른 개발자들에게 영감을 주는 연사자가 되어보세요.',
                'icon_class': 'fas fa-microphone',
                'link_url': '',
                'link_text': '자세히 보기',
                'order': 3,
                'is_active': True,
            },
            {
                'title': '스폰서 제안',
                'description': '기업이나 단체에서 PyLadies Seoul의 활동을 후원하고 함께 성장해나가요.',
                'icon_class': 'fas fa-handshake',
                'link_url': '',
                'link_text': '자세히 보기',
                'order': 4,
                'is_active': True,
            },
            {
                'title': '협업 제안',
                'description': '다른 커뮤니티나 조직과 함께 더 큰 시너지를 만들어가는 협업을 제안해주세요.',
                'icon_class': 'fas fa-users',
                'link_url': '',
                'link_text': '자세히 보기',
                'order': 5,
                'is_active': True,
            },
            {
                'title': '피드백',
                'description': '이벤트, 웹사이트, 커뮤니티 운영에 대한 소중한 의견을 들려주세요. 여러분의 피드백이 더 나은 PyLadies Seoul을 만듭니다.',
                'icon_class': 'fas fa-comments',
                'link_url': '',
                'link_text': '자세히 보기',
                'order': 6,
                'is_active': True,
            },
        ]

        created_count = 0
        updated_count = 0

        for method_data in contribute_methods:
            contribute_method, created = ContributeMethod.objects.get_or_create(
                title=method_data['title'],
                defaults=method_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created contribute method: {contribute_method.title}')
                )
            else:
                # Update existing record if needed
                updated = False
                for field, value in method_data.items():
                    if getattr(contribute_method, field) != value:
                        setattr(contribute_method, field, value)
                        updated = True
                
                if updated:
                    contribute_method.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Updated contribute method: {contribute_method.title}')
                    )
                else:
                    self.stdout.write(f'- Contribute method already exists: {contribute_method.title}')

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Setup complete! Created: {created_count}, Updated: {updated_count}'
            )
        )
        self.stdout.write('='*50)