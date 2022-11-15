from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Добавление css класса."""
    return field.as_widget(attrs={'class': css})
