from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.order_by('id').all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]