from django.urls import path

from .rest.views import WalletList, ActionList

urlpatterns = [
    path('wallets/', WalletList.as_view(), name='list-wallets'),
    path('actions/', ActionList.as_view(), name='list-actions'),
]
