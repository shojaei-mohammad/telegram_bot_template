class DiscountValidationError(Exception):
    """Base class for exceptions in this module."""

    pass


class DiscountExpiredError(DiscountValidationError):
    """Raised when the discount has expired."""

    pass


class DiscountUsageExceededError(DiscountValidationError):
    """Raised when the discount's usage limit has been exceeded."""

    pass


class DiscountAlreadyUsedError(DiscountValidationError):
    """Raised when the user has already used the discount."""

    pass
