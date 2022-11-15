from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для постов."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Введите текст', 'group': 'Выберите группу'}
        help_text = {'text': 'Напишите ваш пост', 'group': 'Выберите группу'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Добавить комментарий'}
        help_texts = {'text': 'Текст комментария'}
