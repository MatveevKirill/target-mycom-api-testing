class ResponseStatusCodeException(Exception):
    pass


class CannotGetCookieException(Exception):
    pass


class CannotGetCSRFToken(Exception):
    pass


class IncorrectLoginException(Exception):
    pass


class CannotGetJSONAttribute(Exception):
    pass


class InvalidMimeType(Exception):
    pass


class ObjectNotFoundError(Exception):
    pass
