from django import template
from django.conf import settings
from main.translations import get_translation

register = template.Library()


@register.filter
def media_url(path):
    """Для image_url/photo: если путь уже полный (/ или http) — как есть, иначе MEDIA_URL + path."""
    if not path:
        return ''
    path = str(path).strip()
    if path.startswith(('http://', 'https://', '/')):
        return path
    return (settings.MEDIA_URL or '/media/') + path


@register.simple_tag(takes_context=True)
def t(context, text):
    lang = context.get('request').session.get('language', 'ru')
    return get_translation(text, lang)
