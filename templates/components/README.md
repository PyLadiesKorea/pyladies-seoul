# PyLadies Seoul 템플릿 컴포넌트 가이드

이 디렉토리에는 재사용 가능한 템플릿 컴포넌트들이 포함되어 있습니다.

## 사용 가능한 컴포넌트

### 1. page_header.html
페이지 헤더 섹션을 생성합니다.

```django
{% include "components/page_header.html" with title="Page Title" subtitle="Page subtitle" icon="fas fa-icon" %}
```

**매개변수:**
- `title`: 페이지 제목 (필수)
- `subtitle`: 페이지 부제목 (선택)
- `icon`: FontAwesome 아이콘 클래스 (선택)

### 2. breadcrumb.html
브레드크럼 네비게이션을 생성합니다.

```django
{% include "components/breadcrumb.html" with items=breadcrumb_items %}
```

**매개변수:**
- `items`: 브레드크럼 항목들의 리스트 (dict 형태: `{"url": "/path", "title": "Title"}`)

### 3. member_avatar.html
멤버 아바타를 표시합니다.

```django
{% include "components/member_avatar.html" with member=member size="120" class="rounded-circle" %}
```

**매개변수:**
- `member`: 멤버 객체 (필수)
- `size`: 이미지 크기 (기본값: 200)
- `class`: 추가 CSS 클래스 (기본값: "rounded-circle")

### 4. member_badge.html
멤버 타입 배지를 표시합니다.

```django
{% include "components/member_badge.html" with member=member %}
```

**매개변수:**
- `member`: 멤버 객체 (필수)

### 5. social_links.html
소셜 미디어 링크들을 표시합니다.

```django
{% include "components/social_links.html" with member=member %}
```

**매개변수:**
- `member`: 멤버 객체 (필수)

### 6. tags.html
태그/배지들을 표시합니다.

```django
{% include "components/tags.html" with tags=member.tags.all title="Skills & Interests" %}
```

**매개변수:**
- `tags`: 태그 객체들의 리스트 (필수)
- `title`: 섹션 제목 (선택)

### 7. form_field.html
폼 입력 필드를 생성합니다.

```django
{% include "components/form_field.html" with field_name="name" label="Name" type="text" required=True field_value=form.name.value field_error=form.name.errors.0 %}
```

**매개변수:**
- `field_name`: 필드 이름 (필수)
- `label`: 라벨 텍스트 (필수)
- `type`: 입력 타입 (기본값: "text")
- `required`: 필수 필드 여부 (기본값: False)
- `field_value`: 필드 값 (선택)
- `field_error`: 에러 메시지 (선택)
- `rows`: textarea의 행 수 (기본값: 5)

### 8. stat_card.html
통계 카드를 생성합니다.

```django
{% include "components/stat_card.html" with icon="fas fa-users" number="500+" text="Community Members" %}
```

**매개변수:**
- `icon`: FontAwesome 아이콘 클래스 (필수)
- `number`: 통계 숫자 (필수)
- `text`: 설명 텍스트 (필수)

### 9. search_form.html
검색 폼을 생성합니다.

```django
{% include "components/search_form.html" with query=query placeholder="Search content, members..." %}
```

**매개변수:**
- `query`: 검색 쿼리 (선택)
- `placeholder`: 플레이스홀더 텍스트 (기본값: "Search...")

### 10. cta_section.html
콜투액션 섹션을 생성합니다.

```django
{% include "components/cta_section.html" with title="Join Our Community" subtitle="파이썬을 배우고, 네트워킹하고, 함께 성장해요!" primary_btn_text="Get Started" primary_btn_url="/contact/" secondary_btn_text="Meet Members" secondary_btn_url="/members/" %}
```

**매개변수:**
- `title`: 섹션 제목 (기본값: "Join Our Community")
- `subtitle`: 부제목 (기본값: "파이썬을 배우고, 네트워킹하고, 함께 성장해요!")
- `primary_btn_text`: 주요 버튼 텍스트 (선택)
- `primary_btn_url`: 주요 버튼 URL (선택)
- `secondary_btn_text`: 보조 버튼 텍스트 (선택)
- `secondary_btn_url`: 보조 버튼 URL (선택)

### 11. content_type_badge.html
콘텐츠 타입 배지를 생성합니다.

```django
{% include "components/content_type_badge.html" with content=page %}
```

**매개변수:**
- `content`: 콘텐츠 객체 (필수, is_event, is_interview 속성 필요)

### 12. search_result_card.html
검색 결과 카드를 생성합니다.

```django
{% include "components/search_result_card.html" with result=result %}
```

**매개변수:**
- `result`: 검색 결과 객체 (필수, title 속성으로 콘텐츠/멤버 구분)

### 13. content_meta.html
콘텐츠 메타 정보를 표시합니다.

```django
{% include "components/content_meta.html" with content=page %}
```

**매개변수:**
- `content`: 콘텐츠 객체 (필수, publication_date, view_count, reading_time 속성)

### 14. event_info_alert.html
이벤트 정보 알림을 표시합니다.

```django
{% include "components/event_info_alert.html" with event=page %}
```

**매개변수:**
- `event`: 이벤트 객체 (필수, is_event, event_start_at, event_end_at, location 속성)

### 15. social_links_grid.html
소셜 링크 그리드를 표시합니다.

```django
{% include "components/social_links_grid.html" with social_links=social_links %}
```

**매개변수:**
- `social_links`: 소셜 링크 객체들의 리스트 (필수)

### 16. faq_accordion.html
FAQ 아코디언을 표시합니다.

```django
{% include "components/faq_accordion.html" with faq_pages=faq_pages %}
```

**매개변수:**
- `faq_pages`: FAQ 객체들의 리스트 (필수, question, answer 속성)

### 17. contribute_card.html
기여 방법 카드를 생성합니다.

```django
{% include "components/contribute_card.html" with method=method %}
```

**매개변수:**
- `method`: 기여 방법 객체 (필수, icon_class, title, description, link_url, link_text 속성)

### 18. organizer_card.html
조직자 카드를 생성합니다.

```django
{% include "components/organizer_card.html" with organizer=organizer %}
```

**매개변수:**
- `organizer`: 조직자 객체 (필수, photo, name, role 속성)

### 19. event_card.html
이벤트 카드를 생성합니다.

```django
{% include "components/event_card.html" with event=content type="featured" %}
{% include "components/event_card.html" with event=content type="regular" %}
```

**매개변수:**
- `event`: 이벤트 객체 (필수)
- `type`: 카드 타입 - "featured" 또는 "regular" (기본값: "regular")
- `show_status`: 상태 표시 여부 (기본값: True)

### 20. social_share_buttons.html
소셜 공유 버튼을 생성합니다.

```django
{% include "components/social_share_buttons.html" with url=request.build_absolute_uri title=page.title %}
```

**매개변수:**
- `url`: 공유할 URL (필수)
- `title`: 공유할 제목 (필수)
- `platforms`: 공유할 플랫폼 리스트 (기본값: ["twitter", "facebook", "linkedin"])
- `size`: 버튼 크기 - "sm", "md", "lg" (기본값: "sm")
- `class`: 추가 CSS 클래스 (선택)

### 21. interview_info.html
인터뷰 정보를 표시합니다.

```django
{% include "components/interview_info.html" with interview=page %}
```

**매개변수:**
- `interview`: 인터뷰 객체 (필수, is_interview, related_member 속성 필요)
- `show_avatar`: 아바타 표시 여부 (기본값: True)
- `class`: 추가 CSS 클래스 (선택)

### 22. sidebar.html
사이드바를 생성합니다.

```django
{% include "components/sidebar.html" with related_content=related_content category=category %}
```

**매개변수:**
- `related_content`: 관련 콘텐츠 리스트 (선택)
- `category`: 카테고리 객체 (선택)
- `show_related`: 관련 콘텐츠 표시 여부 (기본값: True)
- `show_category`: 카테고리 정보 표시 여부 (기본값: True)
- `show_quick_actions`: 빠른 액션 표시 여부 (기본값: True)
- `class`: 추가 CSS 클래스 (선택)

### 23. content_grid.html
콘텐츠 그리드를 생성합니다.

```django
{% include "components/content_grid.html" with contents=content_pages %}
```

**매개변수:**
- `contents`: 콘텐츠 리스트 (필수)
- `columns`: 그리드 컬럼 수 - 2, 3, 4 (기본값: 3)
- `show_empty_message`: 빈 상태 메시지 표시 여부 (기본값: True)
- `empty_message`: 빈 상태 메시지 (기본값: "No content found")
- `empty_icon`: 빈 상태 아이콘 (기본값: "fas fa-search")
- `class`: 추가 CSS 클래스 (선택)

### 24. search_tips.html
검색 팁을 표시합니다.

```django
{% include "components/search_tips.html" %}
```

**매개변수:**
- `show_quick_links`: 빠른 링크 표시 여부 (기본값: True)
- `class`: 추가 CSS 클래스 (선택)

### 25. content_grid_items.html
콘텐츠 그리드 아이템들을 렌더링합니다.

```django
{% include "components/content_grid_items.html" with contents=contents %}
```

**매개변수:**
- `contents`: 콘텐츠 리스트 (필수)
- `columns`: 그리드 컬럼 수 - 2, 3, 4 (기본값: 3)
- `show_empty_message`: 빈 상태 메시지 표시 여부 (기본값: True)
- `empty_message`: 빈 상태 메시지 (기본값: "No content found")
- `empty_icon`: 빈 상태 아이콘 (기본값: "fas fa-search")
- `class`: 추가 CSS 클래스 (선택)

## 접근성 및 SEO 개선사항

### ARIA 라벨 및 역할
- 모든 폼 요소에 적절한 `aria-label` 추가
- 시맨틱 HTML 태그 사용 (`<article>`, `<section>`, `<header>`, `<footer>`, `<nav>`, `<main>`, `<aside>`)
- `role` 속성으로 요소의 역할 명시
- `aria-labelledby`로 제목과 콘텐츠 연결

### 키보드 네비게이션
- 모든 인터랙티브 요소가 키보드로 접근 가능
- 포커스 표시가 명확하게 보임
- 논리적인 탭 순서

### 스크린 리더 지원
- `aria-hidden="true"`로 장식용 아이콘 숨김
- `aria-live`로 동적 콘텐츠 변경 알림
- `aria-current`로 현재 페이지 표시

### 구조화된 데이터
- Schema.org 마크업 추가 (브레드크럼, 이벤트 정보)
- `itemprop` 속성으로 메타데이터 제공
- `datetime` 속성으로 시간 정보 구조화

## 사용 예시

### 페이지 헤더와 브레드크럼
```django
{% extends "base.html" %}

{% block content %}
    {% include "components/page_header.html" with title="About Us" subtitle="우리의 이야기를 들어보세요" icon="fas fa-info-circle" %}
    
    {% with breadcrumb_items=breadcrumb_items|default:"[{'url': '/about/', 'title': 'About'}]" %}
        {% include "components/breadcrumb.html" with items=breadcrumb_items %}
    {% endwith %}
    
    <!-- 페이지 내용 -->
{% endblock %}
```

### 멤버 카드
```django
<div class="member-card">
    {% include "components/member_avatar.html" with member=member size="200" %}
    {% include "components/member_badge.html" with member=member %}
    {% include "components/social_links.html" with member=member %}
    {% include "components/tags.html" with tags=member.tags.all %}
</div>
```

### 폼
```django
<form method="post">
    {% csrf_token %}
    {% include "components/form_field.html" with field_name="name" label="Name" type="text" required=True field_value=form.name.value field_error=form.name.errors.0 %}
    {% include "components/form_field.html" with field_name="email" label="Email" type="email" required=True field_value=form.email.value field_error=form.email.errors.0 %}
    {% include "components/form_field.html" with field_name="message" label="Message" type="textarea" required=True field_value=form.message.value field_error=form.message.errors.0 %}
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

## 템플릿 태그 사용법

### 콘텐츠 필터링 태그

```django
{% load content_tags %}

<!-- 이벤트만 필터링 -->
{% with events=contents|filter_events %}
    {% for event in events %}
        <!-- 이벤트 처리 -->
    {% endfor %}
{% endwith %}

<!-- 업커밍 이벤트만 필터링 -->
{% with upcoming=contents|filter_upcoming_events %}
    {% for event in upcoming %}
        <!-- 업커밍 이벤트 처리 -->
    {% endfor %}
{% endwith %}

<!-- 과거 이벤트만 필터링 -->
{% with past=contents|filter_past_events %}
    {% for event in past %}
        <!-- 과거 이벤트 처리 -->
    {% endfor %}
{% endwith %}

<!-- 이벤트가 아닌 콘텐츠만 필터링 -->
{% with non_events=contents|filter_non_events %}
    {% for content in non_events %}
        <!-- 비이벤트 콘텐츠 처리 -->
    {% endfor %}
{% endwith %}
```

### 이벤트 상태 태그

```django
{% load content_tags %}

<!-- 이벤트 상태 확인 -->
{% get_event_status event as status %}

<!-- 이벤트 상태에 따른 CSS 클래스 -->
<div class="card-header {% get_event_status_class event %}">
    <small>
        <i class="{% get_event_status_icon event %}" aria-hidden="true"></i> 
        {% get_event_status_text event %}
    </small>
</div>
```

### 조건부 확인 태그

```django
{% load content_tags %}

<!-- 업커밍 이벤트가 있는지 확인 -->
{% if contents|has_upcoming_events %}
    <!-- 업커밍 이벤트 섹션 표시 -->
{% endif %}

<!-- 과거 이벤트가 있는지 확인 -->
{% if contents|has_past_events %}
    <!-- 과거 이벤트 섹션 표시 -->
{% endif %}
```

## 유지보수 가이드

1. **새 컴포넌트 추가 시**: README.md에 사용법을 문서화하세요.
2. **기존 컴포넌트 수정 시**: 하위 호환성을 유지하세요.
3. **매개변수 변경 시**: 기본값을 제공하여 기존 사용처가 깨지지 않도록 하세요.
4. **CSS 클래스 변경 시**: 기존 스타일과의 호환성을 확인하세요.
5. **템플릿 태그 추가 시**: `apps/content/templatetags/content_tags.py`에 추가하고 문서화하세요.
