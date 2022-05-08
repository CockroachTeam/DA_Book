from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import PostSerializer, UserSerializer
from .models import Post
from rest_framework import permissions, mixins,generics



class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer