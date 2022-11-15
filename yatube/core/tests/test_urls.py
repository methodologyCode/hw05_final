from django.test import TestCase, Client


class CoreURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_template_url_create(self):
        url = '/unexisting_page/'
        template = 'core/404.html'
        response = self.guest_client.get(url)
        self.assertTemplateUsed(response, template)
