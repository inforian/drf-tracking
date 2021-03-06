from .models import APIRequestLog
from django.utils.timezone import now
import traceback


class BaseLoggingMixin(object):
    logging_methods = '__all__'
    sensitive_fields = {}

    """Mixin to log requests"""
    def initial(self, request, drf_request, *args, **kwargs):
        # get IP
        http_request_obj = request
        request = drf_request

        ipaddr = request.META.get("HTTP_X_FORWARDED_FOR", None)
        if ipaddr:
            # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
            ipaddr = [x.strip() for x in ipaddr.split(",")][0]
        else:
            ipaddr = request.META.get("REMOTE_ADDR", "")

        # get view
        view_name = ''
        try:
            method = request.method.lower()
            attributes = getattr(self, method)
            view_name = (type(attributes.__self__).__module__ + '.' +
                         type(attributes.__self__).__name__)
        except Exception:
            pass

        # get the method of the view
        if hasattr(self, 'action'):
            view_method = self.action if self.action else ''
        else:
            view_method = method.lower()

        # create log
        qm = self._clean_data(http_request_obj.GET.dict())

        self.log = APIRequestLog(
            requested_at=now(),
            path=request.path,
            view=view_name,
            view_method=view_method,
            remote_addr=ipaddr,
            host=request.get_host(),
            method=request.method,
            query_params=qm,
        )

        # regular initial, including auth check
        if kwargs.get('middleware') is not True:
            super(BaseLoggingMixin, self).initial(http_request_obj, *args, **kwargs)

        # add user to log after auth
        user = request.user

        if user.is_anonymous():
            user = None
        self.log.user = user

        data_ = http_request_obj.POST.dict()

        # data_.update({
        #     'POST': http_request_obj.POST.dict(),
        #     'files': http_request_obj.FILES
        # })
        self.log.data = self._clean_data(data_)

        # try:
        #     # Accessing request.data *for the first time* parses the request body, which may raise
        #     # ParseError and UnsupportedMediaType exceptions. It's important not to swallow these,
        #     # as (depending on implementation details) they may only get raised this once, and
        #     # DRF logic needs them to be raised by the view for error handling to work correctly.
        #     self.log.data = self._clean_data(data_.dict())
        # except AttributeError:  # if already a dict, can't dictify
        #     self.log.data = self._clean_data(data_)

    def handle_exception(self, exc, **kwargs):
        # log error
        if hasattr(self, 'log'):
            self.log.errors = traceback.format_exc()

        # basic handling
        if kwargs.get('middleware') is not True:
            return super(BaseLoggingMixin, self).handle_exception(exc)

    def finalize_response(self, request, response, *args, **kwargs):
        # regular finalize response
        if kwargs.get('middleware') is not True:
            response = super(BaseLoggingMixin, self).finalize_response(request, response, *args, **kwargs)

        # check if request is being logged
        if not hasattr(self, 'log'):
            return response

        # compute response time
        response_timedelta = now() - self.log.requested_at
        response_ms = int(response_timedelta.total_seconds() * 1000)

        # save to log

        if (self._should_log(request, response)):
            try:
                self.log.response = response.rendered_content
                self.log.status_code = response.status_code
                self.log.response_ms = response_ms
            except:
                pass
            try:
                self.log.save()
            except Exception:
                # ensure that a DB error doesn't prevent API call to continue as expected
                pass

        # return
        return response

    def _should_log(self, request, response):
        """
        Method that should return True if this request should be logged.
        By default, check if the request method is in logging_methods.
        """
        return self.logging_methods == '__all__' or request.method in self.logging_methods

    def _clean_data(self, data):
        """
        Clean a dictionary of data of potentially sensitive info before
        sending to the database.
        Function based on the "_clean_credentials" function of django
        (https://github.com/django/django/blob/stable/1.11.x/django/contrib/auth/__init__.py#L50)

        Fields defined by django are by default cleaned with this function

        You can define your own sensitive fields in your view by defining a set
        eg: sensitive_fields = {'field1', 'field2'}
        """
        data = dict(data)

        SENSITIVE_FIELDS = {'api', 'token', 'key', 'secret', 'password', 'signature',
                            'old_password', 'csrfmiddlewaretoken', 'new_password'}
        CLEANED_SUBSTITUTE = '********************'

        if self.sensitive_fields:
            SENSITIVE_FIELDS = SENSITIVE_FIELDS | {field.lower() for field in self.sensitive_fields}

        for key in data:
            if key.lower() in SENSITIVE_FIELDS:
                data[key] = CLEANED_SUBSTITUTE
        return data


class LoggingMixin(BaseLoggingMixin):
    pass


class LoggingErrorsMixin(BaseLoggingMixin):
    """
    Log only errors
    """
    def _should_log(self, request, response):
        return response.status_code >= 400
