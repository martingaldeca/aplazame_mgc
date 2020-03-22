from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_202_ACCEPTED, HTTP_406_NOT_ACCEPTABLE
from rest_framework.views import APIView
from apps.finance.exceptions import InsufficientFundsException, InvalidAmount, WrongTokenError

from apps.finance.transactions import add_funds

from logging import getLogger

logger = getLogger(__name__)


class AddFunds(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.needed_fields = ['amount_to_add', 'token']
        self.ok_message = 'Funds added.'

    def post(self, request, format=None):
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

        amount_to_add = request_data.get('amount_to_add', None)
        token = request_data.get('token', None)
        comment = request_data.get('comment', None)
        test_sleep_time = request_data.get('test_sleep_time', 0)
        try:
            add_funds(amount_to_add=amount_to_add, token=token, comment=comment, test_sleep_time=test_sleep_time)
        except WrongTokenError as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidAmount as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_406_NOT_ACCEPTABLE)
        except Exception as ex:
            content = {"error": str(ex)}
            return Response(content, status=HTTP_500_INTERNAL_SERVER_ERROR)

        content = {"ok": self.ok_message}
        return Response(content, status=HTTP_202_ACCEPTED)
