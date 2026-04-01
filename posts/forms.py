from django import forms
from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class PostForm(forms.ModelForm):
    allowed_usernames = forms.CharField(
        required=False,
        label='Allowed usernames (comma-separated)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. john, naima, arif'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'visibility', 'allowed_usernames']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'visibility': forms.RadioSelect(choices=Post.VISIBILITY_CHOICES),
        }

    def clean(self):
        cleaned_data = super().clean()
        visibility = cleaned_data.get('visibility')
        usernames = cleaned_data.get('allowed_usernames', '') or ''
        username_list = [u.strip() for u in usernames.split(',') if u.strip()]

        if visibility == 'specific':
            if not username_list:
                raise forms.ValidationError('For specific visibility, provide at least one valid username.')

            valid_users = []
            invalid_users = []
            for uname in username_list:
                try:
                    user = User.objects.get(username=uname)
                    valid_users.append(user)
                except User.DoesNotExist:
                    invalid_users.append(uname)

            if invalid_users:
                raise forms.ValidationError(f"These users do not exist: {', '.join(invalid_users)}")

            cleaned_data['allowed_user_objects'] = valid_users
        else:
            cleaned_data['allowed_user_objects'] = []

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
