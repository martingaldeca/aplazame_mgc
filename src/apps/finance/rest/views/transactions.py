from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_202_ACCEPTED, HTTP_406_NOT_ACCEPTABLE, HTTP_402_PAYMENT_REQUIRED
)
from rest_framework.views import APIView
from apps.finance.exceptions import InsufficientFundsException, InvalidAmount, WrongTokenError
from apps.core.exceptions import NotCommerceError

from apps.finance.transactions import add_funds, add_charge

from logging import getLogger

logger = getLogger(__name__)


class CommonTransactionApi(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.needed_fields = []
        self.ok_message = 'ok.'
        self.all_transaction_args = {}

    def post(self, request):
        # Get the data from the post
        request_data = request.data

        # The post must be very specific, so we must check that we have needed fields
        not_passed_elements = [field for field in self.needed_fields if field not in request_data.keys()]
        if len(not_passed_elements) > 0:
            logger.error(f"Bad format in post.")
            content = {
                "error": (
                    f"The post need the fields {self.needed_fields} but "
                    f"did not pass {not_passed_elements} fields."
                )
            }
            return Response(content, status=HTTP_400_BAD_REQUEST)

        # with this avoid to pass extra parameters that can be posted
        for key in self.all_transaction_args.keys():
            self.all_transaction_args[key] = request_data.get(key, None)

        bad_response_to_use = self.try_transaction(self.all_transaction_args)
        if bad_response_to_use is not None:
            return bad_response_to_use

        content = {"ok": self.ok_message}
        return Response(content, status=HTTP_202_ACCEPTED)

    @staticmethod
    def try_transaction(transaction_args: dict = None):
        """
        Overwrite this method in each transaction api implemented
        :param transaction_args:
        :return:
        """
        pass


class AddFunds(CommonTransactionApi):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.needed_fields = ['amount_to_add', 'token']
        self.ok_message = 'Funds added.'
        self.all_transaction_args = {'amount_to_add': None, 'token': None, 'comment': None}

    @staticmethod
    def try_transaction(transaction_args: dict = None):
        try:
            add_funds(**transaction_args)
        except WrongTokenError as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidAmount as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_406_NOT_ACCEPTABLE)
        except Exception as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_500_INTERNAL_SERVER_ERROR)


class AddCharge(CommonTransactionApi):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.needed_fields = ['amount_to_charge', 'creditor_token', 'debtor_token']
        self.ok_message = 'Transaction complete.'
        self.all_transaction_args = {
            'amount_to_charge': None, 'creditor_token': None, 'debtor_token': None, 'comment': None
        }

    @staticmethod
    def try_transaction(transaction_args: dict = None):

        try:
            add_charge(**transaction_args)
        except WrongTokenError as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidAmount as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_406_NOT_ACCEPTABLE)
        except NotCommerceError as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_406_NOT_ACCEPTABLE)
        except InsufficientFundsException as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_402_PAYMENT_REQUIRED)
        except Exception as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_500_INTERNAL_SERVER_ERROR)

