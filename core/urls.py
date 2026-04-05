from django.contrib import admin
from django.urls import path, include
from posts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('my-posts/', views.MyPostsView.as_view(), name='my_posts'),
    path('profile/', views.profile, name='profile'),
]