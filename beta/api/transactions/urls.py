from django.urls import path


from . import views


urlpatterns = [
    path('import', views.import_csv, name='import_csv'),
]