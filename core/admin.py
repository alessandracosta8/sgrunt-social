"""
Imports:
"""
from django.contrib import admin
from .models import Post, Comment, UserProfile


# So we can view it in the admin page
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserProfile)
