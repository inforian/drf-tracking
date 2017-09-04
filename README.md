# drf-tracking

[![build-status-image]][travis]
[![pypi-version]][pypi]
[![Requirements Status](https://requires.io/github/aschn/drf-tracking/requirements.svg?branch=master)](https://requires.io/github/aschn/drf-tracking/requirements/?branch=master)

## Overview

drf-tracking provides a Django model and DRF view mixin that work together to log Django Rest Framework requests to the database. You'll get these attributes for every request/response cycle to a view that uses the mixin:

 Model field name | Description | Model field type
------------------|-------------|-----------------
`user` | User if authenticated, None if not | Foreign Key
`requested_at` | Date-time that the request was made | DateTimeField
`response_ms` | Number of milliseconds spent in view code | PositiveIntegerField
`path` | Target URI of the request, e.g., `"/api/"` | CharField
`view` | Target VIEW of the request, e.g., `"views.api.ApiView"` | CharField
`view_method` | Target METHOD of the VIEW of the request, e.g., `"get"` | CharField
`remote_addr` | IP address where the request originated (X_FORWARDED_FOR if available, REMOTE_ADDR if not), e.g., `"127.0.0.1"` | GenericIPAddressField
`host` | Originating host of the request, e.g., `"example.com"` | URLField
`method` | HTTP method, e.g., `"GET"` | CharField
`query_params` | Dictionary of request query parameters, as text | TextField
`data` | Dictionary of POST data (JSON or form), as text | TextField
`response` | JSON response data | TextField
`status_code` | HTTP status code, e.g., `200` or `404` | PositiveIntegerField


## Requirements

* Django 1.8, 1.9, 1.10, 1.11
* Django REST Framework and Python release supporting the version of Django you are using

## Installation

Install using `pip`...

```bash
$ pip install drf-tracking
```


## for middleware support
- install this fork using pip install -e git+git://github.com/inforian/drf-tracking.git@master#egg=drf-tracking
- Add `'rest_framework_tracking.middleware.DrfTrackingMiddleware'` in settings.
- Follow other instructions as mentioned below.

Register with your Django project by adding `rest_framework_tracking`
to the `INSTALLED_APPS` list in your project's `settings.py` file.
Then run the migrations for the `APIRequestLog` model:

```bash
$ python manage.py migrate
```

## Usage

Add the `rest_framework_tracking.mixins.LoggingMixin` to any DRF view
to create an instance of `APIRequestLog` every time the view is called.

For instance:
```python
# views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

class LoggingView(LoggingMixin, generics.GenericAPIView):
    def get(self, request):
        return Response('with logging')
```

For performance enhancement, explicitly choose methods to be logged using `logging_methods` attribute:
```python
class LoggingView(LoggingMixin, generics.CreateModelMixin, generics.GenericAPIView):
    logging_methods = ['POST', 'PUT']
    model = ...
```

## Security

By default drf-tracking is hidding the values of those fields `{'api', 'token', 'key', 'secret', 'password', 'signature'}`.
The default list hast been taken from Django itself ([https://github.com/django/django/blob/stable/1.11.x/django/contrib/auth/__init__.py#L50](https://github.com/django/django/blob/stable/1.11.x/django/contrib/auth/__init__.py#L50)).

You can complet this list with your own list by putting the fields you want to be hidden in the `sensitive_fields` parameter of your view

```python
class LoggingView(LoggingMixin, generics.CreateModelMixin, generics.GenericAPIView):
    sensitive_fields = {'my_secret_key', 'my_secret_recipe'}
```

## Testing

Install testing requirements.

```bash
$ pip install -r requirements.txt
```

Run with runtests.

```bash
$ ./runtests.py
```

You can also use the excellent [tox](http://tox.readthedocs.org/en/latest/) testing tool to run the tests against all supported versions of Python and Django. Install tox globally, and then simply run:

```bash
$ tox
```

## Documentation

To build the documentation, you'll need to install `mkdocs`.

```bash
$ pip install mkdocs
```

To preview the documentation:

```bash
$ mkdocs serve
Running at: http://127.0.0.1:8000/
```

To build the documentation:

```bash
$ mkdocs build
```


[build-status-image]: https://secure.travis-ci.org/aschn/drf-tracking.png?branch=master
[travis]: http://travis-ci.org/aschn/drf-tracking?branch=master
[pypi-version]: https://img.shields.io/pypi/v/drf-tracking.svg
[pypi]: https://pypi.python.org/pypi/drf-tracking
