import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Проза',
            slug='test_slug')

        cls.group_test = Group.objects.create(
            title='поэма',
            slug='test')

        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""

        IMAGE = 'posts/small.gif'
        posts_count = Post.objects.count()

        # Создание с картинкой.
        form_data = {
            'text': 'Пост 2',
            'group': PostCreateFormTests.group.id,
            'image': PostCreateFormTests.uploaded
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': 'test'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создался наш пост.
        self.assertTrue(
            Post.objects.filter(
                text='Пост 2',
                author=PostCreateFormTests.user,
                group=PostCreateFormTests.group,
                image=IMAGE
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирования поста."""

        IMG = 'posts/another.gif'
        post = PostCreateFormTests.post

        gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='another.gif',
            content=gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'изменился',
            'group': PostCreateFormTests.group_test.id,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse("posts:post_edit",
                    kwargs=({'post_id': post.id})),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={
                                         'post_id': post.id
                                     }))
        # Проверяем, изменился ли пост.
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            pk=PostCreateFormTests.post.pk,
            author=PostCreateFormTests.user,
            group=PostCreateFormTests.group_test,
            image=IMG).exists())

    def test_create_check_fields_form(self):
        """Проверка полей формы на принадлежность экземплярам."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Проверка коммента
    def test_create_comment_form(self):
        """Проверка добавления нового комментария."""

        comments_count = Comment.objects.filter(
            post=PostCreateFormTests.post.pk
        ).count()

        form_data = {
            'text': 'test-comment',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={
                        'post_id': PostCreateFormTests.post.pk
                    }
                    ),
            data=form_data,
            follow=True
        )
        comments = Post.objects.filter(
            id=PostCreateFormTests.post.pk
        ).values_list('comments', flat=True)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': PostCreateFormTests.post.pk
                }
            )
        )
        self.assertEqual(
            comments.count(),
            comments_count + 1
        )
        self.assertTrue(
            Comment.objects.filter(
                author=PostCreateFormTests.user,
                post=PostCreateFormTests.post.pk,
                text=form_data['text']
            ).exists()
        )
