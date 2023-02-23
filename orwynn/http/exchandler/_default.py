class DefaultErrorHandler(ExceptionHandler):
    E = Error

    def handle(self, request: HttpRequest, error: Error) -> HttpResponse:
        return JsonHttpResponse(error.api, 400)


class DefaultRequestValidationExceptionHandler(ExceptionHandler):
    E = RequestValidationException

    def handle(
        self,
        request: HttpRequest,
        error: RequestValidationException
    ) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            422
        )


class DefaultExceptionHandler(ExceptionHandler):
    E = Exception

    def handle(self, request: HttpRequest, error: Exception) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            400
        )


class DefaultHttpExceptionHandler(ExceptionHandler):
    E = HttpException

    def handle(
        self, request: HttpRequest, error: HttpException
    ) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            error.status_code
        )
