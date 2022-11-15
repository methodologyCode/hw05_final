import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug')

        cls.test_group = Group.objects.create(title='Тестовая группа 2',
                                              slug='testing_group')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

        cls.count = Post.objects.all().count()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'test'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка контекста.
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        index_text_0 = first_object.text
        index_author_0 = first_object.author
        index_group_0 = first_object.group
        # Картинка.
        index_img = first_object.image
        self.assertEqual(index_text_0, PostsPagesTests.post.text)
        self.assertEqual(index_author_0, PostsPagesTests.user)
        self.assertEqual(index_group_0, PostsPagesTests.group)
        self.assertEqual(index_img, PostsPagesTests.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{PostsPagesTests.group.slug}'}))
        context_group = response.context.get('group')
        group_title = context_group.title
        group_slug = context_group.slug
        # Картинка.
        context_post_image = response.context['page_obj'][0].image
        self.assertEqual(group_title, PostsPagesTests.group.title)
        self.assertEqual(group_slug, PostsPagesTests.group.slug)
        self.assertEqual(context_group, PostsPagesTests.group)
        self.assertEqual(context_post_image, PostsPagesTests.post.image)

        two_object = response.context['page_obj'][0]
        post_text = two_object.text
        post_author = two_object.author
        post_group = two_object.group
        self.assertEqual(post_text, PostsPagesTests.post.text)
        self.assertEqual(post_author, PostsPagesTests.user)
        self.assertEqual(post_group, PostsPagesTests.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{PostsPagesTests.user.username}'}))
        object = response.context['page_obj'][0]
        post_text = object.text
        post_group = object.group
        post_author = object.author
        # Картинка.
        post_image = object.image
        amount = response.context['amount']
        author = response.context['author']
        self.assertEqual(post_text, PostsPagesTests.post.text)
        self.assertEqual(post_group, PostsPagesTests.group)
        self.assertEqual(post_author, PostsPagesTests.user)
        self.assertEqual(amount, PostsPagesTests.count)
        self.assertEqual(author.username, PostsPagesTests.user.username)
        self.assertEqual(post_image, PostsPagesTests.post.image)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{PostsPagesTests.post.pk}'})))
        context = response.context.get('post')
        self.assertEqual(context.text,
                         PostsPagesTests.post.text)
        self.assertEqual(context.author,
                         PostsPagesTests.user)
        self.assertEqual(context.group,
                         PostsPagesTests.group)
        # Картинка.
        self.assertEqual(context.image,
                         PostsPagesTests.post.image)

    def test_create_post_form(self):
        """Является экземпляром формы PostForm."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        is_edit = response.context.get('is_edit')
        # is_edit = False/None
        self.assertFalse(is_edit)

    def test_edit_post_form(self):
        """Является экземпляром формы PostForm."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': PostsPagesTests.post.pk}))
        form = response.context.get('form')
        is_edit = response.context.get('is_edit')
        self.assertIsInstance(form, PostForm)
        self.assertEqual(is_edit, True)

    def test_post_added_right(self):
        """Пост при создании не добавляется в другую группу."""
        posts_count_another_group = Post.objects.filter(
            group=PostsPagesTests.test_group).count()

        posts_count = Post.objects.filter(
            group=PostsPagesTests.group).count()

        self.assertNotEqual(posts_count, posts_count_another_group)

    # Проверка доступности формы.
    def test_to_comment_form_guest(self):
        """Если гость, то False."""
        response = self.guest_client.get(
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': PostsPagesTests.post.pk}))
        form_comment = response.context.get('user').is_authenticated
        self.assertFalse(form_comment)

    def test_to_comment_form_authorized(self):
        """Если авторизован, то True."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': PostsPagesTests.post.pk}))
        form_comment = response.context.get('user').is_authenticated
        self.assertTrue(form_comment)

    def test_cache_on_main_page(self):
        """Проверка кэша."""
        post = Post.objects.create(
            text='Testing',
            author=PostsPagesTests.user,
            group=PostsPagesTests.group,
        )
        response_first = self.authorized_client.get(reverse('posts:index'))
        posts = response_first.content
        post.delete()
        response_two = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_two.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_author = Client()
        self.guest = Client()
        self.user_follower = User.objects.create_user(username='follower')
        self.user_author = User.objects.create_user(username='author')
        self.post = Post.objects.create(
            author=self.user_author,
            text='Тестовая запись'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_author.force_login(self.user_author)

    def test_auth_follow_and_unfollow(self):
        """Тестирование подписки и отписки."""
        self.client_auth_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_author.username}))
        self.assertEqual(Follow.objects.all().count(), 1)

        self.client_auth_follower.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_author.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_feed(self):
        """Тестирование ленты подписчиков."""
        self.client_auth_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_author.username}))
        response = self.client_auth_follower.get(reverse('posts:follow_index'))
        post_text = response.context["page_obj"][0].text
        self.assertEqual(post_text, self.post.text)

        response = self.client_auth_author.get(reverse('posts:follow_index'))
        self.assertNotContains(response, self.post.text)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        start, end = 1, 21
        cls.amount = 10
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug')
        posts = [Post(text='111',
                      author=cls.user,
                      group=cls.group) for _ in range(start, end)]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_posts(self):
        urls = (
            reverse("posts:index"),
            reverse("posts:group_list",
                    kwargs={"slug": f"{PaginatorViewsTest.group.slug}"}),
            reverse("posts:profile",
                    kwargs={"username": f"{PaginatorViewsTest.user.username}"})
        )
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(len(response.context.get('page_obj').object_list),
                             PaginatorViewsTest.amount)

    def test_two_page_contains_five_posts(self):
        urls = [
            reverse("posts:index") + "?page=2",
            reverse("posts:group_list",
                    kwargs={"slug": f"{PaginatorViewsTest.group.slug}"})
            + "?page=2",
            reverse("posts:profile",
                    kwargs={"username": f"{PaginatorViewsTest.user.username}"})
            + "?page=2"
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(len(response.context.get('page_obj').object_list),
                             PaginatorViewsTest.amount)
