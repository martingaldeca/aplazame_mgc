from django.urls import path

from .rest.views import WalletList, ActionList, AddFunds

urlpatterns = [
    path('wallets/', WalletList.as_view(), name='list-wallets'),
    path('actions/', ActionList.as_view(), name='list-actions'),
    path('add_funds/', AddFunds.as_view(), name='add-funds'),
]
