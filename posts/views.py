from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.http import HttpResponseForbidden
from .models import Post
from .forms import PostForm, UserProfileForm

# Custom Login View - Ignores 'next' parameter and always redirects to home
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Always redirect to home, completely ignore any 'next' parameter
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


# Class-based views with proper authorization

class HomeView(ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_queryset(self):
        posts = super().get_queryset()
        user = self.request.user

        # Filter posts based on visibility
        readable_posts = []
        for post in posts:
            if user.is_authenticated:
                if post.is_readable_by(user):
                    readable_posts.append(post)
            else:
                if post.visibility == 'public':
                    readable_posts.append(post)

        return readable_posts


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check visibility permissions
        if not request.user.is_authenticated:
            if self.object.visibility != 'public':
                return redirect('login')
        else:
            if not self.object.is_readable_by(request.user):
                messages.error(request, 'You do not have permission to view this post.')
                return redirect('home')

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # Handle allowed users for specific visibility
        if self.object.visibility == 'specific':
            allowed_users = form.cleaned_data.get('allowed_user_objects', [])
            self.object.allowed_users.set(allowed_users)
        else:
            self.object.allowed_users.clear()

        # Redirect to post detail instead of home
        self.success_url = reverse_lazy('post_detail', kwargs={'pk': self.object.pk})
        return response


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def test_func(self):
        """Check if user is the author of the post"""
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        """Handle unauthorized access"""
        if not self.request.user.is_authenticated:
            return redirect('login')
        return HttpResponseForbidden("You don't have permission to edit this post.")

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        """Pre-populate allowed_usernames field"""
        initial = super().get_initial()
        if self.object.visibility == 'specific':
            existing_usernames = ', '.join(self.object.allowed_users.values_list('username', flat=True))
            initial['allowed_usernames'] = existing_usernames
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)

        # Handle allowed users for specific visibility
        if self.object.visibility == 'specific':
            allowed_users = form.cleaned_data.get('allowed_user_objects', [])
            self.object.allowed_users.set(allowed_users)
        else:
            self.object.allowed_users.clear()

        return response


# Function-based views (keeping register, my_posts, and profile for now)

# 2. Register View: Notun user account kholar jonno
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Register korar por direct login hoye jabe
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# 6. Delete Post View: Author nijei delete korte parbe
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    template_name = 'posts/post_confirm_delete.html'  # We'll need to create this template

    def test_func(self):
        """Check if user is the author of the post"""
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        """Handle unauthorized access"""
        if not self.request.user.is_authenticated:
            return redirect('login')
        return HttpResponseForbidden("You don't have permission to delete this post.")

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Your post has been successfully deleted.')
        return super().delete(request, *args, **kwargs)

class MyPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/my_posts.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
        elif 'change_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            if not check_password(old_password, user.password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password1 != new_password2:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password1) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            else:
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Password changed successfully!')
                return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user)

    return render(request, 'posts/profile.html', {'profile_form': profile_form})
