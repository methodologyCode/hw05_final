from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Follow(models.Model):
    """Подсписки."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')


class Post(models.Model):
    """Посты."""
    text = models.TextField('Содержание', help_text='Введите текст')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='Автор')
    group = models.ForeignKey('Group', blank=True, null=True,
                              on_delete=models.SET_NULL,
                              related_name='post', verbose_name='Группа',
                              help_text='Группа, к которой относиться пост')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """Изменение поведения модели."""
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """Читабельность объекта."""
        return self.text[:15]


class Group(models.Model):
    """Группы."""
    title = models.CharField(max_length=200, verbose_name='Название',
                             help_text='Введите название')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание',
                                   help_text='Введите описание')

    def __str__(self):
        """Читабельность объекта."""
        return self.title


class Comment(models.Model):
    """Комментарии пользователей."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('Содержание', help_text='Введите текст')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self):
        """Читабельность объекта."""
        return self.text
