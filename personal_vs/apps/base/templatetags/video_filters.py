from django import template

register = template.Library()


@register.filter
def format_duration(seconds):
    if not seconds:
        return "00:00"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"

    return f"{minutes:02d}:{remaining_seconds:02d}"