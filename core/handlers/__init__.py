# handlers/__init__.py


def initialize_handlers():
    from core.handlers.messages import registration_handler, default_message_handler
    from core.handlers.callbacks import defualt_callback_handler
    from core.handlers import inline_query_handler
