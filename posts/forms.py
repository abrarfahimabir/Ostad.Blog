from django import forms
from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class PostForm(forms.ModelForm):
    allowed_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Users to Share With"
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'visibility', 'allowed_users']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'visibility': forms.RadioSelect(choices=Post.VISIBILITY_CHOICES),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
