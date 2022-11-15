from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, который нужно проверить',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        post = PostModelTest.post
        expected_object_name = 'Тестовый пост, '
        self.assertEqual(expected_object_name, str(post))

        group = PostModelTest.group
        expected_object_title = group.title
        self.assertEqual(expected_object_title, str(group))

    def test_title_labels(self):
        """Проверка verbose_name's полей text/title."""
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        expected_object_verbose_name = 'Содержание'
        self.assertEqual(verbose, expected_object_verbose_name)

        group = PostModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        expected_object_name = 'Название'
        self.assertEqual(verbose, expected_object_name)

    def test_title_help_text(self):
        """Проверка help_text полей text/title."""
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        expected_help_text = 'Введите текст'
        self.assertEqual(help_text, expected_help_text)

        group = PostModelTest.group
        help_text = group._meta.get_field('title').help_text
        expected_text = 'Введите название'
        self.assertEqual(help_text, expected_text)
