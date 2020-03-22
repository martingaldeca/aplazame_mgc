from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from apps.finance.models import Wallet, Action


@admin.register(Wallet)
class DistributorAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'user', 'token', 'name', 'description', 'balance', 'currency')
    list_select_related = ('user', )
    search_fields = ('user', 'token', 'name')
    readonly_fields = ('balance', 'currency', 'token')
    list_filter = ('currency', )
    raw_id_fields = ('user', )


@admin.register(Action)
class DistributorAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'created_by', 'created', 'wallet', 'action_type', 'delta')
    list_select_related = ('created_by', 'wallet')
    search_fields = ('created_by', 'wallet', 'delta', 'created')
    list_filter = ('action_type', )
    raw_id_fields = ('created_by', 'wallet')
