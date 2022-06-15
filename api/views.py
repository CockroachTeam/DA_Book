from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from api.pagination import CustomPageNumberPagination
from api.serializers import TodoSerializer
from rest_framework.permissions import IsAuthenticated
from api.models import Todo
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class TodosAPIView(ListCreateAPIView):
    serializer_class = TodoSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAuthenticated,)
    filter_backends=[DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]

    filterset_fields = ['id','title','desc','is_complete']
    search_fields = ['id','title','desc','is_complete']
    ordering_fields = ['id','title','desc','is_complete']

# 데이터 받아서 만들기 (POST)
    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)

#리스트 보기 (GET)
    def get_queryset(self):
        return Todo.objects.filter(owner=self.request.user)

#삭제 업데이트
class TodoDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field="id"

    def get_queryset(self):
        return Todo.objects.filter(owner=self.request.user)