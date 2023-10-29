# handlers/__init__.py


def initialize_handlers():
    from . import (
        cancel_state_handler,
        registration_handler,
    )
    from .callbacks import defualt
