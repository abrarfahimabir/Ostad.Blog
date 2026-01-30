from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200) # Blog er title
    content = models.TextField()             # Blog er bhetorer lekha
    author = models.ForeignKey(User, on_delete=models.CASCADE) # User delete hole post o delete hobe
    created_at = models.DateTimeField(auto_now_add=True)       # Automatic date nibe
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title