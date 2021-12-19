from django.db import models
from uuid import uuid4

class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    title = models.CharField(max_length=256)

    file_name = models.CharField(max_length=256)
    file_date = models.DateTimeField()
    add_date = models.DateTimeField()
    page = models.IntegerField()
    sha1 = models.CharField(max_length=64)
    size = models.BigIntegerField()

    def __str__(self):
        return f'{self.pk}: {str(self.title)}'
    
    __repr__ = __str__


class Author(models.Model):
    name = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return f'{self.pk}: {str(self.name)}'
    
    __repr__ = __str__