from django import template
from django.utils import timezone
from typing import List, Dict, Any

register = template.Library()


@register.filter
def filter_upcoming_events(contents: List[Any]) -> List[Any]:
    """
    현재 날짜 이후의 이벤트만 필터링합니다.
    """
    current_date = timezone.now()
    return [
        content for content in contents 
        if hasattr(content, 'is_event') and content.is_event 
        and hasattr(content, 'event_start_at') and content.event_start_at 
        and content.event_start_at >= current_date
    ]


@register.filter
def filter_past_events(contents: List[Any]) -> List[Any]:
    """
    현재 날짜 이전의 이벤트만 필터링합니다.
    """
    current_date = timezone.now()
    return [
        content for content in contents 
        if hasattr(content, 'is_event') and content.is_event 
        and hasattr(content, 'event_start_at') and content.event_start_at 
        and content.event_start_at < current_date
    ]


@register.filter
def filter_events(contents: List[Any]) -> List[Any]:
    """
    이벤트만 필터링합니다.
    """
    return [
        content for content in contents 
        if hasattr(content, 'is_event') and content.is_event
    ]


@register.filter
def filter_non_events(contents: List[Any]) -> List[Any]:
    """
    이벤트가 아닌 콘텐츠만 필터링합니다.
    """
    return [
        content for content in contents 
        if not (hasattr(content, 'is_event') and content.is_event)
    ]


@register.simple_tag
def get_event_status(event) -> str:
    """
    이벤트의 상태를 반환합니다 (upcoming/past).
    """
    if not hasattr(event, 'event_start_at') or not event.event_start_at:
        return 'unknown'
    
    current_date = timezone.now()
    return 'upcoming' if event.event_start_at >= current_date else 'past'


@register.simple_tag
def get_event_status_class(event) -> str:
    """
    이벤트 상태에 따른 CSS 클래스를 반환합니다.
    """
    status = get_event_status(event)
    return 'bg-primary text-white' if status == 'upcoming' else 'bg-secondary text-white'


@register.simple_tag
def get_event_status_icon(event) -> str:
    """
    이벤트 상태에 따른 아이콘을 반환합니다.
    """
    status = get_event_status(event)
    return 'fas fa-calendar-plus' if status == 'upcoming' else 'fas fa-history'


@register.simple_tag
def get_event_status_text(event) -> str:
    """
    이벤트 상태에 따른 텍스트를 반환합니다.
    """
    status = get_event_status(event)
    return 'Upcoming Event' if status == 'upcoming' else 'Past Event'


@register.filter
def has_upcoming_events(contents: List[Any]) -> bool:
    """
    업커밍 이벤트가 있는지 확인합니다.
    """
    return len(filter_upcoming_events(contents)) > 0


@register.filter
def has_past_events(contents: List[Any]) -> bool:
    """
    과거 이벤트가 있는지 확인합니다.
    """
    return len(filter_past_events(contents)) > 0

