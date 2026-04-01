from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Post
from .forms import PostForm, UserProfileForm

# 1. Home View: Sob blog post eksathe dekhar jonno
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    
    # Filter posts based on visibility
    readable_posts = []
    for post in posts:
        if request.user.is_authenticated:
            if post.is_readable_by(request.user):
                readable_posts.append(post)
        else:
            if post.visibility == 'public':
                readable_posts.append(post)
    
    return render(request, 'posts/home.html', {'posts': readable_posts})

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
    
    # Check visibility permissions
    if not request.user.is_authenticated:
        if post.visibility != 'public':
            return redirect('login')
    else:
        if not post.is_readable_by(request.user):
            messages.error(request, 'You do not have permission to view this post.')
            return redirect('home')
    
    return render(request, 'posts/post_detail.html', {'post': post})

# 4. Create Post View: Login kora user-ra post likhte parbe
@login_required
def post_create(request):
    selected_user_ids = []
    if request.method == "POST":
        form = PostForm(request.POST)
        selected_user_ids = request.POST.getlist('allowed_users')
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Handle allowed_users for specific visibility
            if post.visibility == 'specific':
                allowed_users = form.cleaned_data.get('allowed_users', [])
                post.allowed_users.set(allowed_users)
            else:
                post.allowed_users.clear()
            
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {
        'form': form,
        'selected_user_ids': selected_user_ids,
    })

# 5. Update Post View: Shudhu author nijei edit korte parbe
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Check: Onno keu jeno edit korte na pare
    if post.author != request.user:
        return redirect('home')
    
    selected_user_ids = []
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        selected_user_ids = request.POST.getlist('allowed_users')
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            
            # Handle allowed_users for specific visibility
            if post.visibility == 'specific':
                allowed_users = form.cleaned_data.get('allowed_users', [])
                post.allowed_users.set(allowed_users)
            else:
                post.allowed_users.clear()
            
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
        selected_user_ids = list(post.allowed_users.values_list('id', flat=True))

    return render(request, 'posts/post_form.html', {
        'form': form,
        'selected_user_ids': selected_user_ids,
    })

# 6. Delete Post View: Author nijei delete korte parbe
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Check: Author chara keu delete korte parbe na
    if post.author == request.user:
        post.delete()
        messages.success(request, 'আপনার পোস্টটি সফলভাবে ডিলিট হয়েছে।')
    return redirect('home')

@login_required
def my_posts(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'posts/my_posts.html', {'posts': user_posts})

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
