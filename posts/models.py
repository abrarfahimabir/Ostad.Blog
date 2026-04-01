from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    VISIBILITY_CHOICES = [
        ('private', 'Only Me'),
        ('specific', 'Specific Users'),
        ('public', 'Everyone'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # New visibility fields
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    allowed_users = models.ManyToManyField(User, related_name='shared_posts', blank=True)

    def __str__(self):
        return self.title
    
    def is_readable_by(self, user):
        """Check if a user can read this post"""
        if self.visibility == 'public':
            return True
        if self.author == user:
            return True
        if self.visibility == 'private':
            return False
        if self.visibility == 'specific':
            return self.allowed_users.filter(pk=user.pk).exists()
        return False
