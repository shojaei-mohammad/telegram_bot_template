# handlers/__init__.py


def initialize_handlers():
    from . import registration_handler, default_handlers
    from .callbacks import defualt, inline_query_handler
