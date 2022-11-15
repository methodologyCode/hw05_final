from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Страница о авторе."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Страница о скиллах."""
    template_name = 'about/tech.html'
