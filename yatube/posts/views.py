from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Group, Post, User, Follow
from .forms import CommentForm, PostForm

AMOUNT = 10


def index(request):
    """Показывает список постов и групп,если есть."""
    template = 'posts/index.html'
    post_list = Post.objects.select_related('group').all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, AMOUNT)
    # Из URL извлекаем номер запрошенной страницы.
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    """Показывает группу постов по общей тематике."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.post.select_related('author').all()
    paginator = Paginator(post_list, AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'group': group}
    return render(request, template, context)


def profile(request, username):
    """Страница пользователя."""
    author = User.objects.get(username=username)
    posts = author.posts.select_related('author').all()
    paginator = Paginator(posts, AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
    else:
        following = False

    context = {
        'author': author,
        'page_obj': page_obj,
        'amount': posts.count(),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница конкретного поста."""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    amount = post.author.posts.count()
    form = CommentForm()
    context = {
        'form': form,
        'post': post,
        'amount': amount,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    """Создание поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    )


@login_required()
def post_edit(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True

    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': is_edit})


@login_required
def add_comment(request, post_id):
    """Комментарии."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


# posts/views.py

@login_required
def follow_index(request):
    """Подписки."""
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page_obj': page}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not is_follower.exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=username)

