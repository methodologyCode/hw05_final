def test_template_url_create(self):
    """Проверка кастомного шаблона 404."""
    url = '/unexisting_page/'
    template = 'core/404.html'
    response = self.authorized_client.get(url)
    self.assertTemplateUsed(response, template)
