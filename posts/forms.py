from django import forms
from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content'] # Author amra logic diye set korbo

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
