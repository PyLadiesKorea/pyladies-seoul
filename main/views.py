import re
from typing import Any, Dict, Optional

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import FAQ, Activity, ContributionOpportunity, Organizer, SocialMediaPlatform

# 커뮤니티 상수 정보
COMMUNITY_INFO: Dict[str, str] = {
    "name_ko": "파이레이디스 서울",
    "name_en": "PyLadies Seoul",
    "vision_ko": ("모든 여성이 파이썬 커뮤니티에서 환영받고 성장할 수 있는 환경을 만듭니다."),
    "vision_en": ("Creating an environment where all women are welcomed and can " "grow in the Python community."),
    "mission_ko": ("파이썬을 사용하는 여성 개발자들의 네트워킹, 학습, 성장을 지원합니다."),
    "mission_en": ("Supporting networking, learning, and growth for women Python " "developers."),
    "email": "seoul@pyladies.com",
}

# Code of Conduct 상수 정보 (Python Software Foundation 기반)
CODE_OF_CONDUCT: Dict[str, str] = {
    "title_ko": "행동 강령",
    "title_en": "Code of Conduct",
    "description_ko": (
        "PyLadies Korea의 모든 구성원, 발표자, 후원사, 자원봉사자는 "
        "다음 행동 강령을 준수할 것을 요청받습니다. 주최자는 이 규칙을 "
        "모든 행사 기간 동안 시행할 것입니다. 우리는 모든 참가자에게 안전한 "
        "환경을 보장하기 위해 협조를 기대합니다."
    ),
    "description_en": (
        "All members, speakers, sponsors and volunteers at any PyLadies Korea "
        "event are required to agree with the following code of conduct. "
        "Organizers will enforce this code throughout the event. We are "
        "expecting cooperation from all participants to help ensuring a safe "
        "environment for everybody."
    ),
    "community_title_ko": "파이썬 커뮤니티",
    "community_title_en": "The Python Community",
    "community_content_ko": (
        "파이썬 커뮤니티의 구성원들은 **개방적이고, 사려 깊으며, 존중합니다**. "
        "이러한 가치를 강화하는 행동은 긍정적인 환경에 기여하며, 다음을 포함합니다:\n\n"
        "• **개방적이기**: 커뮤니티 구성원들은 PEP, 패치, 문제 등 모든 면에서 "
        "협업에 열려 있습니다.\n"
        "• **커뮤니티에 최선인 것에 집중하기**: 우리는 커뮤니티에 정해진 절차를 "
        "존중하며 그 안에서 활동합니다.\n"
        "• **시간과 노력을 인정하기**: 우리는 파이썬 커뮤니티에 널리 퍼져 있는 "
        "자원봉사 노력을 존중합니다.\n"
        "• **다양한 관점과 경험을 존중하기**: 우리는 건설적인 의견과 비판을 수용합니다.\n"
        "• **다른 커뮤니티 구성원들에게 공감하기**: 우리는 대면이든 온라인이든 "
        "소통에서 세심하게 주의를 기울입니다.\n"
        "• **사려 깊기**: 커뮤니티 구성원들은 동료들 - 다른 Python 사용자들을 "
        "배려합니다.\n"
        "• **존중하기**: 우리는 다른 사람들, 그들의 입장, 기술, 헌신, 노력을 "
        "존중합니다.\n"
        "• **건설적인 비판을 우아하게 받아들이기**: 우리가 동의하지 않을 때, "
        "우리는 이슈를 제기할 때 정중합니다.\n"
        "• **환영하고 포용적인 언어 사용하기**: 우리는 우리 활동에 참여하고자 하는 "
        "모든 사람을 받아들입니다."
    ),
    "community_content_en": (
        "Members of the Python community are **open, considerate, and "
        "respectful**. Behaviours that reinforce these values contribute to a "
        "positive environment, and include:\n\n"
        "• **Being open**: Members of the community are open to collaboration, "
        "whether it's on PEPs, patches, problems, or otherwise.\n"
        "• **Focusing on what is best for the community**: We're respectful of "
        "the processes set forth in the community, and we work within them.\n"
        "• **Acknowledging time and effort**: We're respectful of the "
        "volunteer efforts that permeate the Python community.\n"
        "• **Being respectful of differing viewpoints and experiences**: We're "
        "receptive to constructive comments and criticism.\n"
        "• **Showing empathy towards other community members**: We're attentive "
        "in our communications, whether in person or online.\n"
        "• **Being considerate**: Members of the community are considerate of "
        "their peers – other Python users.\n"
        "• **Being respectful**: We're respectful of others, their positions, "
        "their skills, their commitments, and their efforts.\n"
        "• **Gracefully accepting constructive criticism**: When we disagree, "
        "we are courteous in raising our issues.\n"
        "• **Using welcoming and inclusive language**: We're accepting of all "
        "who wish to take part in our activities."
    ),
    "standards_title_ko": "우리의 기준",
    "standards_title_en": "Our Standards",
    "standards_content_ko": (
        "우리 커뮤니티의 모든 구성원은 자신의 정체성을 존중받을 권리가 있습니다. "
        "Python 커뮤니티는 나이, 성별 정체성과 표현, 성적 지향, 장애, 신체적 "
        "외모, 체형, 민족, 국적, 인종, 종교(또는 종교 없음), 교육, 또는 "
        "사회경제적 지위에 관계없이 모든 사람에게 긍정적인 경험을 제공하기 위해 "
        "노력합니다."
    ),
    "standards_content_en": (
        "Every member of our community has the right to have their identity "
        "respected. The Python community is dedicated to providing a positive "
        "experience for everyone, regardless of age, gender identity and "
        "expression, sexual orientation, disability, physical appearance, "
        "body size, ethnicity, nationality, race, or religion (or lack "
        "thereof), education, or socio-economic status."
    ),
    "inappropriate_title_ko": "부적절한 행동",
    "inappropriate_title_en": "Inappropriate Behavior",
    "inappropriate_content_ko": (
        "참가자의 허용되지 않는 행동의 예는 다음과 같습니다:\n\n"
        "• 어떤 형태로든 참가자에 대한 괴롭힘\n"
        "• 고의적인 협박, 스토킹, 또는 따라다니기\n"
        "• 괴롭힘 목적으로 온라인 활동을 기록하거나 스크린샷 찍기\n"
        "• 명시적 허가 없이 타인의 개인 정보(물리적 또는 전자적 주소 등) 게시\n"
        "• 다른 사람을 향한 폭력적 위협이나 언어\n"
        "• 자살하거나 자해하도록 격려하는 것을 포함하여 개인에 대한 폭력이나 "
        "괴롭힘 선동\n"
        "• 다른 사람을 괴롭히거나 금지를 우회하기 위해 추가 온라인 계정 생성\n"
        "• 온라인 커뮤니티나 컨퍼런스 장소에서 성적 언어와 이미지 사용\n"
        "• 고정관념에 기반한 모욕, 비하, 또는 농담\n"
        "• 과도한 욕설\n"
        "• 원치 않는 성적 관심이나 접근\n"
        "• 동의 없이 또는 중단 요청 후에도 하는 원치 않는 신체적 접촉\n"
        "• 타인과 부적절한 수준의 친밀감을 요구하거나 가정하는 부적절한 사회적 "
        "접촉 패턴\n"
        "• 온라인 커뮤니티 토론, 대면 프레젠테이션, 또는 기타 대면 이벤트의 "
        "지속적인 방해\n"
        "• 중단 요청 후에도 계속되는 일대일 소통\n"
        "• 다양한 배경을 가진 사람들을 포함한 전문적인 청중에게 부적절한 기타 행동"
    ),
    "inappropriate_content_en": (
        "Examples of unacceptable behavior by participants include:\n\n"
        "• Harassment of any participants in any form\n"
        "• Deliberate intimidation, stalking, or following\n"
        "• Logging or taking screenshots of online activity for harassment "
        "purposes\n"
        "• Publishing others' private information without explicit permission\n"
        "• Violent threats or language directed against another person\n"
        "• Incitement of violence or harassment towards any individual\n"
        "• Creating additional online accounts to harass another person or "
        "circumvent a ban\n"
        "• Sexual language and imagery in online communities or conference "
        "venues\n"
        "• Insults, put downs, or jokes that are based upon stereotypes\n"
        "• Excessive swearing\n"
        "• Unwelcome sexual attention or advances\n"
        "• Unwelcome physical contact without consent or after a request to "
        "stop\n"
        "• Pattern of inappropriate social contact\n"
        "• Sustained disruption of online community discussions or in-person "
        "events\n"
        "• Continued one-on-one communication after requests to cease\n"
        "• Other conduct inappropriate for a professional audience"
    ),
    "consequences_title_ko": "결과",
    "consequences_title_en": "Consequences",
    "consequences_content_ko": (
        "참가자가 이 행동 강령을 위반하는 행동에 참여하는 경우, "
        "PyLadies 행동 강령 팀은 가해자에 대한 경고나 커뮤니티 및 커뮤니티 "
        "이벤트에서의 퇴장(이벤트 티켓 환불 없음)을 포함하여 적절하다고 "
        "판단되는 모든 조치를 취할 수 있습니다."
    ),
    "consequences_content_en": (
        "If a participant engages in behavior that violates this code of "
        "conduct, the PyLadies Code of Conduct team may take any action they "
        "deem appropriate, including warning the offender or expulsion from "
        "the community and community events with no refund of event tickets."
    ),
    "contact_title_ko": "연락처 정보",
    "contact_title_en": "Contact Information",
    "contact_content_ko": (
        "누군가가 행동 강령을 위반하고 있다고 생각되거나 다른 우려 사항이 있다면, "
        "즉시 PyLadies 행동 강령 작업 그룹의 구성원에게 연락하십시오. "
        "seoul@pyladies.com으로 이메일을 보내실 수 있습니다."
    ),
    "contact_content_en": (
        "If you believe that someone is violating the code of conduct, or have "
        "any other concerns, please contact a member of the PyLadies Code of "
        "Conduct working group immediately. They can be reached by emailing "
        "seoul@pyladies.com."
    ),
    "source_ko": "이 행동 강령은 Python Software Foundation에서 수정되었습니다.",
    "source_en": ("This Code of Conduct has been adapted from the Python Software " "Foundation."),
    "license_ko": ("Creative Commons Attribution-ShareAlike 3.0 Unported License"),
    "license_en": ("Creative Commons Attribution-ShareAlike 3.0 Unported License"),
    "psf_url": "https://www.python.org/psf/conduct/",
    "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
    "pyladies_coc_email": "seoul@pyladies.com",
}


def get_social_media_platforms() -> QuerySet[SocialMediaPlatform]:
    """활성화된 소셜 미디어 플랫폼 조회"""
    return SocialMediaPlatform.objects.filter(is_active=True).order_by("order")


def get_discord_url() -> Optional[str]:
    """Discord URL 조회"""
    discord_platform = SocialMediaPlatform.objects.filter(name_en__icontains="discord", is_active=True).first()
    return discord_platform.url if discord_platform else None


def convert_markdown_to_html(text: str) -> str:
    """간단한 마크다운을 HTML로 변환"""
    # **굵게** -> <strong>굵게</strong>
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # *기울임* -> <em>기울임</em>
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    # 줄바꿈 처리
    text = text.replace("\n", "<br>")
    return text


def home(request: HttpRequest) -> HttpResponse:
    """홈페이지"""
    now = timezone.now()

    # 다가오는 이벤트 (현재 시간 이후 또는 진행 중인 이벤트)
    upcoming_events = Activity.objects.filter(
        is_public=True,
        start_datetime__gte=now,
    ).order_by(
        "start_datetime"
    )[:6]

    # 지난 이벤트 (현재 시간 이전에 끝난 이벤트)
    past_events = Activity.objects.filter(
        is_public=True,
        start_datetime__lt=now,
    ).order_by(
        "-start_datetime"
    )[:6]

    context: Dict[str, Any] = {
        "community_info": COMMUNITY_INFO,
        "social_platforms": get_social_media_platforms(),
        "discord_url": get_discord_url(),
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "organizers": Organizer.objects.filter(is_public=True)[:6],
    }
    return render(request, "index.html", context)


def contribute(request: HttpRequest) -> HttpResponse:
    """기여하기 페이지"""
    context: Dict[str, Any] = {
        "community_info": COMMUNITY_INFO,
        "social_platforms": get_social_media_platforms(),
        "discord_url": get_discord_url(),
        "opportunities": ContributionOpportunity.objects.filter(is_public=True).order_by("order"),
    }
    return render(request, "contribute.html", context)


def faq(request: HttpRequest) -> HttpResponse:
    """FAQ 페이지"""
    context: Dict[str, Any] = {
        "community_info": COMMUNITY_INFO,
        "social_platforms": get_social_media_platforms(),
        "discord_url": get_discord_url(),
        "faqs": FAQ.objects.filter(is_public=True).order_by("category", "order"),
    }
    return render(request, "faq.html", context)


def coc(request: HttpRequest) -> HttpResponse:
    """행동 강령 페이지"""
    from django.utils.safestring import mark_safe

    # 마크다운 변환이 필요한 필드들
    processed_coc = CODE_OF_CONDUCT.copy()

    # 커뮤니티 내용 변환
    community_ko = CODE_OF_CONDUCT["community_content_ko"]
    processed_coc["community_content_ko"] = mark_safe(convert_markdown_to_html(community_ko))

    community_en = CODE_OF_CONDUCT["community_content_en"]
    processed_coc["community_content_en"] = mark_safe(convert_markdown_to_html(community_en))

    # 부적절한 행동 내용 변환
    inappropriate_ko = CODE_OF_CONDUCT["inappropriate_content_ko"]
    processed_coc["inappropriate_content_ko"] = mark_safe(convert_markdown_to_html(inappropriate_ko))

    inappropriate_en = CODE_OF_CONDUCT["inappropriate_content_en"]
    processed_coc["inappropriate_content_en"] = mark_safe(convert_markdown_to_html(inappropriate_en))

    context: Dict[str, Any] = {
        "coc_info": processed_coc,
        "community_info": COMMUNITY_INFO,
        "discord_url": get_discord_url(),
    }
    return render(request, "coc.html", context)


def events_list(request: HttpRequest) -> HttpResponse:
    """이벤트 목록 페이지"""
    events = Activity.objects.filter(is_public=True).order_by("-start_datetime")

    context: Dict[str, Any] = {
        "events": events,
        "community_info": COMMUNITY_INFO,
        "discord_url": get_discord_url(),
    }
    return render(request, "events_list.html", context)


def event_detail(request: HttpRequest, event_id: int) -> HttpResponse:
    """이벤트 상세 페이지"""
    event = get_object_or_404(Activity, id=event_id, is_public=True)

    # 같은 유형의 관련 이벤트 (현재 이벤트 제외)
    related_events = (
        Activity.objects.filter(activity_type=event.activity_type, is_public=True)
        .exclude(id=event.id)
        .order_by("-start_datetime")[:3]
    )

    context: Dict[str, Any] = {
        "event": event,
        "related_events": related_events,
        "community_info": COMMUNITY_INFO,
        "social_platforms": get_social_media_platforms(),
        "discord_url": get_discord_url(),
    }
    return render(request, "event_detail.html", context)


def health_check(request: HttpRequest) -> HttpResponse:
    """헬스체크 엔드포인트"""
    import sys

    from django.db import connection
    from django.http import JsonResponse

    try:
        # 데이터베이스 연결 확인
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        health_data = {
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0",
            "python_version": sys.version,
            "database": "connected",
        }

        return JsonResponse(health_data)

    except Exception as e:
        health_data = {
            "status": "unhealthy",
            "timestamp": timezone.now().isoformat(),
            "error": str(e),
            "database": "disconnected",
        }

        return JsonResponse(health_data, status=503)
