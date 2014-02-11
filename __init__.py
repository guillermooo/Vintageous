import logging

import sublime


LOG_LEVEL = None


# XXX: Can't we do this better?
def plugin_loaded():
    global LOG_LEVEL
    LOG_LEVEL = get_logging_level()


def get_logging_level():
    global LOG_LEVEL

    if LOG_LEVEL is not None:
        return LOG_LEVEL

    v = sublime.active_window().active_view()
    level = v.settings().get('vintageous_log_level', 'ERROR')

    return getattr(logging, level.upper(), logging.ERROR)


def get_logger(name):
    global LOG_LEVEL
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger


# XXX: Why don't we use a logging config file?
# Work around ST3 delayed loading of plugins. We cannot call the API until
# after the plugin file has been loaded. We just need the api to retrieve
# the setting indicating the logging level. It's probably best to have
# a proper config file for loggers instead of this.
def local_logger(name):
    """
    Returns a generator that in turn returns a valid logger for @name. Once
    the ST3 API is active, `local_logger` will always return the same
    logger. In the meantime, it will return a logger with a default config so
    calls to it won't fail.
    """
    _logger = None
    def loggers():
        nonlocal _logger
        while True:
            try:
                if _logger is None:
                    _logger = get_logger(name)
                yield _logger
            except TypeError:
                temp_logger = logging.getLogger(name)
                temp_logger.setLevel(logging.ERROR)
                yield temp_logger

    return lambda: next(loggers())

