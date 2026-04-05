from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post

class PostAuthorizationTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

        # Create test posts
        self.post1 = Post.objects.create(
            title='Post by user1',
            content='Content 1',
            author=self.user1,
            visibility='public'
        )
        self.post2 = Post.objects.create(
            title='Post by user2',
            content='Content 2',
            author=self.user2,
            visibility='private'
        )

    def test_post_owner_can_edit(self):
        """Test that post owners can access edit view"""
        client = Client()
        client.login(username='user1', password='pass123')

        response = client.get(reverse('post_edit', kwargs={'pk': self.post1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_edit(self):
        """Test that non-owners get 403 when trying to edit"""
        client = Client()
        client.login(username='user2', password='pass123')

        response = client.get(reverse('post_edit', kwargs={'pk': self.post1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_cannot_edit(self):
        """Test that unauthenticated users are redirected"""
        client = Client()

        response = client.get(reverse('post_edit', kwargs={'pk': self.post1.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_login_ignores_next_parameter(self):
        """Test that login view ignores 'next' parameter and always redirects to home"""
        client = Client()

        response = client.post(reverse('login'), {
            'username': 'user1',
            'password': 'pass123',
            'next': '/some/other/page/'
        })
        # Check that it redirects (status 302)
        self.assertEqual(response.status_code, 302)
        # Check that the redirect location is home, not the next parameter
        self.assertTrue(response['Location'].endswith(reverse('home')))
