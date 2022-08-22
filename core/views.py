"""
Imports:
"""
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from django.views.generic.edit import UpdateView, DeleteView
from .models import Post, Comment
from .forms import PostForm, CommentForm


class PostListView(LoginRequiredMixin, View):
    """
    Post feed view
    """
    def get(self, request, *args, **kwargs):
        """ Iterate through posts and display them from newest to last """
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm()

        context = {
            'post_list': posts,
            'form': form,
        }
        return render(request, 'core/post_list.html', context)

    def post(self, request, *args, **kwargs):
        """ Handles post request and saves the new post """
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm(request.POST)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
        
        context = {
            'post_list': posts,
            'form': form,
        }
        return render(request, 'core/post_list.html', context)


class PostDetailView(LoginRequiredMixin, View):
    """ Post specific page view, with ability to comment and display all comments """
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()
        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        return render(request, 'core/post_detail.html', context)
    
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
        
        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'core/post_detail.html', context)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """ Ability to edit a post """
    model = Post
    fields = ['body']
    template_name = 'core/post_edit.html'

    def get_success_url(self):
        """ redirect to post detail page when edit is successful """
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        """ If user matches post's author -> can edit, or else -> 403 """
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """ Ability to delete post """
    model = Post
    template_name = 'core/post_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        """ If user matches post's author -> can delete, or else -> 403 """
        post = self.get_object()
        return self.request.user == post.author


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """ Ability to delete comment """
    model = Comment
    template_name = 'core/comment_delete.html'

    def get_success_url(self):
        """ redirect to post detail page when comment delete is successful """
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})
    
    def test_func(self):
        """ If user matches comment's author -> can delete, or else -> 403 """
        comment = self.get_object()
        return self.request.user == comment.author
