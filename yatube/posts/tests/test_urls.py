# posts/tests/test_urls.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.not_author = User.objects.create_user(username='another')
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug')

        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_another = Client()
        self.authorized_client_another.force_login(PostsURLTests.not_author)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_posts_urls_exists_at_desired_location(self):
        """Проверка общедоступных страниц."""

        url_names = (
            '/',
            f'/group/{PostsURLTests.group.slug}/',
            f'/profile/{PostsURLTests.user.username}/',
            f'/posts/{PostsURLTests.group.pk}/',
        )
        for url in url_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_noexists_at_undesired_location(self):
        """Проверка несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_author_url_exists_at_desired_location(self):
        """Страница /posts/1/edit/ доступна автору."""
        response = self.authorized_client.get(
            f'/posts/{PostsURLTests.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_redirect(self):
        """Запрос перенаправит гостя на страницу логина."""
        response = self.guest_client.get(
            f'/posts/{PostsURLTests.post.pk}/edit/',
            follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{PostsURLTests.post.pk}/edit/'
        )

    def test_not_author_edit_post_redirect(self):
        """Запрос перенаправит Не автора на страницу поста."""
        response = self.authorized_client_another.get(
            f'/posts/{PostsURLTests.post.pk}/edit/',
            follow=True)
        self.assertRedirects(
            response, f'/posts/{PostsURLTests.post.pk}/'
        )

    def test_create_post_redirect(self):
        """Запрос перенаправит гостя на страницу логина."""
        response = self.guest_client.get('/create/',
                                         follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_urls_uses_correct_templates(self):
        """Адрес использует соответствующий шаблон."""
        templates_urls_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{PostsURLTests.group.slug}/',
            'posts/profile.html': f'/profile/{PostsURLTests.user.username}/',
            'posts/post_detail.html': f'/posts/{PostsURLTests.post.pk}/',
            'posts/create_post.html': f'/posts/{PostsURLTests.post.pk}/edit/'
        }
        for template, url in templates_urls_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_template_url_create(self):
        url = '/create/'
        template = 'posts/create_post.html'
        response = self.authorized_client.get(url)
        self.assertTemplateUsed(response, template)
