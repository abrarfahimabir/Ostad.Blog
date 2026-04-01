from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Post
from .forms import PostForm, UserProfileForm # Eita banate hobe 'posts/forms.py' te

# 1. Home View: Sob blog post eksathe dekhar jonno
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/home.html', {'posts': posts})

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

# 3. Post Detail View: Ekta specific blog purota porar jonno
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'posts/post_detail.html', {'post': post})

# 4. Create Post View: Login kora user-ra post likhte parbe
@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user # Je login ache shei hobe author
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})

# 5. Update Post View: Shudhu author nijei edit korte parbe
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Check: Onno keu jeno edit korte na pare
    if post.author != request.user:
        return redirect('home')
    
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_form.html', {'form': form})

# 6. Delete Post View: Author nijei delete korte parbe
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Check: Author chara keu delete korte parbe na
    if post.author == request.user:
        post.delete()
    
    return redirect('home')

@login_required
def my_posts(request):
    # Shudhu logged in user-er post gulo filter kora hocche
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'posts/my_posts.html', {'posts': user_posts})

from django.shortcuts import render, get_object_or_404
from .models import Post

def post_detail(request, pk):
    # pk (Primary Key) diye database theke specific post ta khuje ber kora hocche
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'posts/post_detail.html', {'post': post})

from django.contrib import messages

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        post.delete()
        messages.success(request, 'আপনার পোস্টটি সফলভাবে ডিলিট হয়েছে।')
    return redirect('my_posts')

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
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Password changed successfully! Please log in again.')
                return redirect('login')
        else:
            profile_form = UserProfileForm(instance=user)
            password_form = PasswordChangeForm(user)
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = PasswordChangeForm(user)
    
    return render(request, 'posts/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
