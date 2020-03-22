from django.urls import path

from .rest.views import WalletList, ActionList, AddFunds, AddCharge, CheckIntegrity, ObtainIntegrity

urlpatterns = [
    path('wallets/', WalletList.as_view(), name='list-wallets'),
    path('actions/', ActionList.as_view(), name='list-actions'),
    path('add_funds/', AddFunds.as_view(), name='add-funds'),
    path('add_charge/', AddCharge.as_view(), name='add-charge'),
    path('check_integrity/', CheckIntegrity.as_view(), name='check-integrity'),
    path('obtain_integrity/', ObtainIntegrity.as_view(), name='obtain-integrity'),
]
