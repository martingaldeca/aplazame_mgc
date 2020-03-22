import time
from collections import OrderedDict
from logging import getLogger
from django.db import models, IntegrityError
from django.db.models import Q, QuerySet

from rest_framework import generics, filters
from rest_framework.exceptions import server_error
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN

logger = getLogger(__name__)


class GenericList(generics.ListCreateAPIView):
    permission_classes = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.model = models.Model
        self.data = {}
        self.objects_to_post = []
        self.searchable_fields = []

        # List of foreign keys fields to use in the query get
        self.deep_fields = []

        # Fields to resolve in case it is a foreign key
        self.fields_to_resolve = {}

        # Identification value to show if needed
        self.identification_value = ''

        # You can define if post are allowed or not for the model
        self.post_allowed = True

    def _set_fields(self):
        """
        With this method we will be able to manage the query of deep fields of the related models of a model
        :return:
        """
        if not self.deep_fields:
            self.fields = self.serializer_class().get_fields().keys()
        else:
            self.fields = self.deep_fields + list(self.serializer_class().get_fields().keys())

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        try:
            # calling parent function to catch all possible exceptions
            return super(GenericList, self).dispatch(request, *args, **kwargs)
        except Exception as ex:
            logger.warning(ex)
            return server_error('Internal error', ex)

    def get_paginated_response(self, data):
        """
        Overwrite the method for the response.

        Now we can add extra metrics if we need them.
        """
        assert self.paginator is not None

        old_response = self.paginator.get_paginated_response(data).data
        final_response = Response(OrderedDict([
            ('count', old_response['count']),
            ('next', old_response['next']),
            ('previous', old_response['previous']),
            ('results', old_response['results']),
        ]))
        return final_response

    def get_queryset(self):
        """
        Overwrite the get_queryset method to use some filters of the model and some searchable fields of the model.
        :return:
        """
        start_time = time.time()
        self._set_fields()

        # Check if there is any query filter
        query_exact = Q()
        for field in self.fields:
            value = self.request.query_params.get(field, None)
            if value is not None:
                value_list = value.split(',')
                # We will treat the query filter as a list of parameters to filter
                if len(value_list) > 1:
                    query_exact = query_exact & Q(**{
                        f'{field}__in': value_list
                    })
                else:
                    query_exact = query_exact & Q(**{
                        str(field): value_list[0]
                    })

        # Check if there is any search in the query
        query_contains = Q()
        search_value = self.request.query_params.get('search', None)
        if search_value is not None:
            for field in self.searchable_fields:
                query_contains = query_contains | Q(**{
                    f'{field}__icontains': search_value
                })

        # Create the queryset to use
        queryset = self.model.objects.filter(query_exact & query_contains)

        end_time = time.time()
        logger.debug(f"Total http request time = {round((end_time - start_time), 3)} s.")
        return queryset

    def post(self, request, *args, **kwargs):
        if self.post_allowed is False:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            logger.error(f"Someone try to post directly to model {self.model.__name__} from '{ip}'.")
            content = {"forbidden": f"You can not post to this entry point. The address: '{ip}' will be investigate."}
            return Response(content, status=HTTP_403_FORBIDDEN)

        start_time = time.time()

        request_data = request.data.get(self.model.__name__, None)
        if request_data is None:
            raise Exception('Malformed json in request body')

        logger.debug(f"Will try to insert {len(request_data)} {self.model.__name__}s.")

        for data in request_data:
            self.data = data

            # Cast the data with the model fields
            self.cast_data_with_model_fields()

            # Resolve the fields to resolve
            self.resolve_fields_to_resolve()

            # Save the data to post in the objects to post list
            self.objects_to_post.append(
                self.model(**self.data)
            )

        logger.debug(f"Will save {len(self.objects_to_post)} {self.model.__name__}s.")
        try:
            self.model.objects.bulk_create(self.objects_to_post, 500)
        except IntegrityError:
            item_list = [item[self.identification_value] for item in request.data[self.model.__name__][:10]]
            error_message = (
                f"Conflict detected trying to post {self.model.__name__}s "
                f"{item_list if len(request.data[self.model.__name__]) <= 10 else f'{item_list} + {len(request.data[self.model.__name__]) - 10}'}"
            )
            return Response({"error": error_message}, status=HTTP_409_CONFLICT)
        logger.debug(f"Total post time: {round((time.time() - start_time), 3)} s.")

        # Create the content to return in the response of the post and return it
        content = {
            "total_created": len(self.objects_to_post),
            "ids_created": [object_to_post.id for object_to_post in self.objects_to_post]
        }
        return Response(content, status=HTTP_200_OK)

    def get_model_fields(self) -> list:
        """
        Function to get model fields that match data passed by POST.
        """
        model = self.model
        data = self.data
        return [(m, data.get(m.name, None)) for m in model._meta.get_fields() if data.get(m.name, None) is not None]

    def cast_data_with_model_fields(self) -> None:
        """
        Function to cast data fields with the model fields types.
        :param self:
        """
        for model_field in self.get_model_fields():
            field_object, value_to_save = model_field

            if field_object.__class__ is models.FloatField and type(value_to_save) is int:
                self.data[field_object.name] = float(value_to_save)

    def resolve_fields_to_resolve(self) -> None:
        """
        Resolve the foreign key values with the resolver specified
        :return:
        """
        for field_to_resolve, values_of_field_to_resolve in self.fields_to_resolve.items():
            # Get the extra parameters to pass to the resolver
            extra_parameters = {}
            for extra_parameter in values_of_field_to_resolve["extra_parameters"]:
                extra_parameters[extra_parameter] = self.data.get(extra_parameter, None)

                # Must pop from data to avoid problems with database
                self.data.pop(extra_parameter, None)

            self.data[field_to_resolve] = values_of_field_to_resolve["resolver"](self.data[field_to_resolve], **extra_parameters)
