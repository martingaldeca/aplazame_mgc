from django.urls import path

from .rest.views import UserProfileList

urlpatterns = [
    path('users/', UserProfileList.as_view(), name='list-users'),
]
