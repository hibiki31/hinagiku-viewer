from django.urls import path


from . import views


urlpatterns = [
    path('<book_uuid>/<int:book_page>', views.index, name='index'),
]