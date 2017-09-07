
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # MiddlewareMixin is depreciated so catch this exception
    MiddlewareMixin = object
from .mixins import LoggingMixin


class DrfTrackingMiddleware(MiddlewareMixin):
    """Log Every Activity of every Request

    """
    drf_logging = LoggingMixin()

    def process_request(self, request):
        # Don;t log in case of superuser
        if request.user.is_superuser:
            return
        self.drf_logging.initial(request, middleware=True)

    def process_exception(self, request, exception, *args, **kwargs):
        """
        """
        # Don;t log in case of superuser

        if request.user.is_superuser:
            return exception
        self.drf_logging.handle_exception(exception, middleware=True)
        return exception

    def process_response(self, request, response):
        # Don;t log in case of superuser
        try:
            if request.user.is_superuser:
                return response
        except:  # catch exception in case of redirect
            pass


        self.drf_logging.finalize_response(request, response, middleware=True)
        return response
