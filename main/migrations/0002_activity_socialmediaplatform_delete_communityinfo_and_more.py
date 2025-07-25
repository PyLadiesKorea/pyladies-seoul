# Generated by Django 5.2.4 on 2025-07-08 04:34

import django.utils.timezone
from django.db import migrations, models

import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name="created"),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name="modified"),
                ),
                (
                    "title_ko",
                    models.CharField(
                        db_comment="Activity title in Korean",
                        max_length=200,
                        verbose_name="제목 (한국어)",
                    ),
                ),
                (
                    "title_en",
                    models.CharField(
                        db_comment="Activity title in English",
                        max_length=200,
                        verbose_name="제목 (영어)",
                    ),
                ),
                (
                    "description_ko",
                    models.TextField(
                        db_comment="Activity detailed description in Korean",
                        verbose_name="설명 (한국어)",
                    ),
                ),
                (
                    "description_en",
                    models.TextField(
                        db_comment="Activity detailed description in English",
                        verbose_name="설명 (영어)",
                    ),
                ),
                (
                    "activity_type",
                    models.CharField(
                        choices=[
                            ("seminar", "세미나"),
                            ("workshop", "워크숍"),
                            ("meetup", "밋업"),
                            ("networking", "네트워킹"),
                            ("study_group", "스터디그룹"),
                        ],
                        db_comment="Activity type (seminar, workshop, meetup, networking, study_group)",
                        default="seminar",
                        max_length=20,
                        verbose_name="활동 유형",
                    ),
                ),
                (
                    "start_datetime",
                    models.DateTimeField(
                        blank=True,
                        db_comment="Event start date and time",
                        null=True,
                        verbose_name="시작 일시",
                    ),
                ),
                (
                    "end_datetime",
                    models.DateTimeField(
                        blank=True,
                        db_comment="Event end date and time",
                        null=True,
                        verbose_name="종료 일시",
                    ),
                ),
                (
                    "location_name_ko",
                    models.CharField(
                        blank=True,
                        db_comment="Event location name in Korean",
                        max_length=200,
                        verbose_name="장소명 (한국어)",
                    ),
                ),
                (
                    "location_name_en",
                    models.CharField(
                        blank=True,
                        db_comment="Event location name in English",
                        max_length=200,
                        verbose_name="장소명 (영어)",
                    ),
                ),
                (
                    "location_address",
                    models.CharField(
                        blank=True,
                        db_comment="Event location detailed address",
                        max_length=300,
                        verbose_name="장소 주소",
                    ),
                ),
                (
                    "location_url",
                    models.URLField(
                        blank=True,
                        db_comment="Online event URL or location-related link",
                        verbose_name="장소 URL",
                    ),
                ),
                (
                    "meeting_schedule_ko",
                    models.CharField(
                        blank=True,
                        db_comment="Study group regular meeting schedule in Korean",
                        help_text="예: 매주 화요일 오후 7시",
                        max_length=200,
                        null=True,
                        verbose_name="정기 모임 일정 (한국어)",
                    ),
                ),
                (
                    "meeting_schedule_en",
                    models.CharField(
                        blank=True,
                        db_comment="Study group regular meeting schedule in English",
                        help_text="예: Every Tuesday 7PM",
                        max_length=200,
                        null=True,
                        verbose_name="정기 모임 일정 (영어)",
                    ),
                ),
                (
                    "is_recruiting",
                    models.BooleanField(
                        db_comment="Whether study group is recruiting members",
                        default=False,
                        verbose_name="모집 중",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        db_comment="Activity representative image",
                        null=True,
                        upload_to="activities/",
                        verbose_name="대표 이미지",
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        db_comment="Whether activity is public",
                        default=True,
                        verbose_name="공개 여부",
                    ),
                ),
                (
                    "is_featured",
                    models.BooleanField(
                        db_comment="Whether activity is featured on main page",
                        default=False,
                        verbose_name="추천 활동",
                    ),
                ),
            ],
            options={
                "verbose_name": "활동",
                "verbose_name_plural": "활동",
                "db_table_comment": "PyLadies Seoul activities (events and study groups)",
                "ordering": ["-start_datetime", "-created"],
            },
        ),
        migrations.CreateModel(
            name="SocialMediaPlatform",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name="created"),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name="modified"),
                ),
                (
                    "name_ko",
                    models.CharField(
                        db_comment="Platform name in Korean",
                        max_length=100,
                        verbose_name="플랫폼명 (한국어)",
                    ),
                ),
                (
                    "name_en",
                    models.CharField(
                        db_comment="Platform name in English",
                        max_length=100,
                        verbose_name="플랫폼명 (영어)",
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        db_comment="Platform URL or invite link",
                        verbose_name="URL",
                    ),
                ),
                (
                    "icon",
                    models.ImageField(
                        blank=True,
                        db_comment="Platform icon or logo",
                        null=True,
                        upload_to="social_media/",
                        verbose_name="아이콘",
                    ),
                ),
                (
                    "icon_class",
                    models.CharField(
                        blank=True,
                        db_comment="CSS class for icon (e.g., Font Awesome class)",
                        help_text="예: fab fa-discord, fab fa-github",
                        max_length=50,
                        verbose_name="아이콘 CSS 클래스",
                    ),
                ),
                (
                    "order",
                    models.IntegerField(
                        db_comment="Display order of platform",
                        default=0,
                        help_text="표시 순서",
                        verbose_name="표시 순서",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_comment="Whether platform is active and should be displayed",
                        default=True,
                        verbose_name="활성 상태",
                    ),
                ),
            ],
            options={
                "verbose_name": "소셜 미디어 플랫폼",
                "verbose_name_plural": "소셜 미디어 플랫폼",
                "db_table_comment": "PyLadies Seoul social media platforms and external links",
                "ordering": ["order", "name_ko"],
            },
        ),
        migrations.DeleteModel(
            name="CommunityInfo",
        ),
        migrations.DeleteModel(
            name="Event",
        ),
        migrations.DeleteModel(
            name="StudyGroup",
        ),
        migrations.AlterModelOptions(
            name="contributionopportunity",
            options={
                "ordering": ["order", "type", "title_ko"],
                "verbose_name": "기여 기회",
                "verbose_name_plural": "기여 기회",
            },
        ),
        migrations.AlterModelOptions(
            name="faq",
            options={
                "ordering": ["category", "order"],
                "verbose_name": "FAQ",
                "verbose_name_plural": "FAQ",
            },
        ),
        migrations.AlterModelOptions(
            name="organizer",
            options={
                "ordering": ["order", "name_ko"],
                "verbose_name": "오거나이저",
                "verbose_name_plural": "오거나이저",
            },
        ),
        migrations.AlterModelTableComment(
            name="contributionopportunity",
            table_comment="PyLadies Seoul community contribution opportunities",
        ),
        migrations.AlterModelTableComment(
            name="faq",
            table_comment="PyLadies Seoul frequently asked questions",
        ),
        migrations.AlterModelTableComment(
            name="organizer",
            table_comment="PyLadies Seoul organizer information",
        ),
        migrations.RemoveField(
            model_name="contributionopportunity",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="contributionopportunity",
            name="updated_at",
        ),
        migrations.RemoveField(
            model_name="faq",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="faq",
            name="updated_at",
        ),
        migrations.RemoveField(
            model_name="organizer",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="organizer",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="contributionopportunity",
            name="created",
            field=django_extensions.db.fields.CreationDateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="created",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="contributionopportunity",
            name="modified",
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name="modified"),
        ),
        migrations.AddField(
            model_name="contributionopportunity",
            name="order",
            field=models.IntegerField(
                db_comment="Display order of contribution opportunity",
                default=0,
                help_text="표시 순서",
                verbose_name="표시 순서",
            ),
        ),
        migrations.AddField(
            model_name="faq",
            name="created",
            field=django_extensions.db.fields.CreationDateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="created",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="faq",
            name="modified",
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name="modified"),
        ),
        migrations.AddField(
            model_name="organizer",
            name="created",
            field=django_extensions.db.fields.CreationDateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="created",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organizer",
            name="modified",
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name="modified"),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="contact_method_en",
            field=models.TextField(
                db_comment="Contribution opportunity contact method in English",
                verbose_name="연락 방법 (영어)",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="contact_method_ko",
            field=models.TextField(
                db_comment="Contribution opportunity contact method in Korean",
                verbose_name="연락 방법 (한국어)",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="description_en",
            field=models.TextField(
                db_comment="Contribution opportunity description in English",
                verbose_name="설명 (영어)",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="description_ko",
            field=models.TextField(
                db_comment="Contribution opportunity description in Korean",
                verbose_name="설명 (한국어)",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="is_open",
            field=models.BooleanField(
                db_comment="Whether contribution opportunity is open for recruitment",
                default=True,
                verbose_name="모집 중",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="is_public",
            field=models.BooleanField(
                db_comment="Whether contribution opportunity is public",
                default=True,
                verbose_name="공개 여부",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="requirements_en",
            field=models.TextField(
                blank=True,
                db_comment="Contribution opportunity requirements in English",
                verbose_name="요구사항 (영어)",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="requirements_ko",
            field=models.TextField(
                blank=True,
                db_comment="Contribution opportunity requirements in Korean",
                verbose_name="요구사항 (한국어)",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="title_en",
            field=models.CharField(
                db_comment="Contribution opportunity title in English",
                max_length=200,
                verbose_name="제목 (영어)",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="title_ko",
            field=models.CharField(
                db_comment="Contribution opportunity title in Korean",
                max_length=200,
                verbose_name="제목 (한국어)",
            ),
        ),
        migrations.AlterField(
            model_name="contributionopportunity",
            name="type",
            field=models.CharField(
                choices=[
                    ("maker", "메이커"),
                    ("speaker", "스피커"),
                    ("study_leader", "스터디 리더"),
                    ("sponsor", "스폰서"),
                    ("volunteer", "봉사자"),
                    ("donor", "기부"),
                    ("other", "기타"),
                ],
                db_comment="Contribution opportunity type",
                max_length=20,
                verbose_name="기여 유형",
            ),
        ),
        migrations.AlterField(
            model_name="faq",
            name="answer_en",
            field=models.TextField(db_comment="FAQ answer in English", verbose_name="답변 (영어)"),
        ),
        migrations.AlterField(
            model_name="faq",
            name="answer_ko",
            field=models.TextField(db_comment="FAQ answer in Korean", verbose_name="답변 (한국어)"),
        ),
        migrations.AlterField(
            model_name="faq",
            name="category",
            field=models.CharField(
                choices=[
                    ("general", "일반"),
                    ("joining", "참여"),
                    ("participation", "활동"),
                    ("technical", "기술"),
                    ("contact", "연락처"),
                ],
                db_comment="FAQ category",
                default="general",
                max_length=20,
                verbose_name="카테고리",
            ),
        ),
        migrations.AlterField(
            model_name="faq",
            name="is_public",
            field=models.BooleanField(
                db_comment="Whether FAQ is public",
                default=True,
                verbose_name="공개 여부",
            ),
        ),
        migrations.AlterField(
            model_name="faq",
            name="order",
            field=models.IntegerField(
                db_comment="Display order of FAQ",
                default=0,
                help_text="표시 순서",
                verbose_name="표시 순서",
            ),
        ),
        migrations.AlterField(
            model_name="faq",
            name="question_en",
            field=models.CharField(
                db_comment="FAQ question in English",
                max_length=200,
                verbose_name="질문 (영어)",
            ),
        ),
        migrations.AlterField(
            model_name="faq",
            name="question_ko",
            field=models.CharField(
                db_comment="FAQ question in Korean",
                max_length=200,
                verbose_name="질문 (한국어)",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="bio_en",
            field=models.TextField(
                blank=True,
                db_comment="Organizer bio in English",
                verbose_name="소개 (영어)",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="bio_ko",
            field=models.TextField(
                blank=True,
                db_comment="Organizer bio in Korean",
                verbose_name="소개 (한국어)",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="email",
            field=models.EmailField(
                blank=True,
                db_comment="Organizer contact email",
                max_length=254,
                verbose_name="이메일",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="github",
            field=models.URLField(
                blank=True,
                db_comment="Organizer GitHub profile URL",
                verbose_name="GitHub URL",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="is_public",
            field=models.BooleanField(
                db_comment="Whether organizer is public",
                default=True,
                verbose_name="공개 여부",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="linkedin",
            field=models.URLField(
                blank=True,
                db_comment="Organizer LinkedIn profile URL",
                verbose_name="LinkedIn URL",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="name_en",
            field=models.CharField(
                db_comment="Organizer name in English",
                max_length=100,
                verbose_name="이름 (영어)",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="name_ko",
            field=models.CharField(
                db_comment="Organizer name in Korean",
                max_length=100,
                verbose_name="이름 (한국어)",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="order",
            field=models.IntegerField(
                db_comment="Display order of organizer",
                default=0,
                help_text="표시 순서",
                verbose_name="표시 순서",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="photo",
            field=models.ImageField(
                blank=True,
                db_comment="Organizer profile photo",
                null=True,
                upload_to="organizers/",
                verbose_name="프로필 사진",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="role_en",
            field=models.CharField(
                db_comment="Organizer role in English",
                max_length=100,
                verbose_name="역할 (영어)",
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="role_ko",
            field=models.CharField(
                db_comment="Organizer role in Korean",
                max_length=100,
                verbose_name="역할 (한국어)",
            ),
        ),
    ]
