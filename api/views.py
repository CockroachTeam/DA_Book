# from django.shortcuts import render
# from django.contrib.auth.models import User
# from rest_framework import viewsets
# from .serializers import PostSerializer, UserSerializer
# from .models import Post
# from rest_framework import permissions, mixins,generics
# from rest_framework.pagination import PageNumberPagination

# # 페이지 네이션 클래스 추가
# class LargeResultsSetPagination(PageNumberPagination):
#     page_size = 100
#     page_size_query_param = 'page_size'
#     max_page_size = 1000

# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 4
#     page_size_query_param = 'page_size'
#     max_page_size = 10


# class PostView(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#     pagination_class = StandardResultsSetPagination
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

# class UserView(viewsets.ReadOnlyModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     pagination_class = StandardResultsSetPagination