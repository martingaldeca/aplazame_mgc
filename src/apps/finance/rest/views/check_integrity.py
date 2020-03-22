from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT
from rest_framework.views import APIView
from apps.finance.models import Wallet
from apps.finance.tasks import check_integrity

from logging import getLogger

logger = getLogger(__name__)


class ObtainIntegrity(APIView):
    """
    Obtain the integrity of the database.
    """

    @staticmethod
    def get(request):
        corrupted_wallets = Wallet.objects.filter(is_corrupted=True)
        if corrupted_wallets.count() > 0:
            content = {'corrupted_wallets': ', '.join([str(wallet_id[0]) for wallet_id in corrupted_wallets.values_list('id')])}
            return Response(content, status=HTTP_200_OK)
        else:
            content = {'ok': 'All wallets are not corrupted'}
            return Response(content, status=HTTP_409_CONFLICT)


class CheckIntegrity(APIView):
    """
    Start the celery task for the integrity of the database
    """

    @staticmethod
    def get(request):
        check_integrity.delay()
        content = {'started': 'The integrity check started'}
        return Response(content, status=HTTP_200_OK)
