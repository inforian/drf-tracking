
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # MiddlewareMixin is depreciated so catch this exception
    MiddlewareMixin = object
from .mixins import LoggingMixin


from rest_framework.views import APIView


class DrfTrackingMiddleware(MiddlewareMixin):
    """Log Every Activity of every Request

    """
    drf_logging = LoggingMixin()

    def _convert_django_request_to_drf_request_object(self, request):
        """convert Django `httpRequest` object into DRF request object

        :param request: Django Http Request Object
        :return: DRF request object
        """
        return APIView().initialize_request(request)

    def process_request(self, request):
        # Don;t log in case of superuser
        if request.user.is_superuser:
            return
        drf_request = self._convert_django_request_to_drf_request_object(request)
        self.drf_logging.initial(request, drf_request, middleware=True)
        return

    def process_exception(self, request, exception, *args, **kwargs):
        """
        """
        # Don;t log in case of superuser

        if request.user.is_superuser:
            return exception
        rq = self._convert_django_request_to_drf_request_object(request)

        self.drf_logging.handle_exception(exception, middleware=True)
        return exception

    def process_response(self, request, response):
        # Don;t log in case of superuser
        try:
            if request.user.is_superuser:
                return response
        except: # catech exception in case of redirect
            pass
        # try:
        #     response.status_code
        # except:
        #     import  ipdb;ipdb.set_trace()

        rq = self._convert_django_request_to_drf_request_object(request)
        self.drf_logging.finalize_response(rq, response, middleware=True)
        return response
