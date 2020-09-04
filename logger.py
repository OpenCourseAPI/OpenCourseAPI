import click


def log(tag, color, message, details=None, pad=True, start='', end='\n'):
    '''
    Log a message to stdout

    :param tag: (str) The tag, ex. `info` or `warn`
    :param color: (str) The color for the tag (passed to colorama)
    :param message: (str) The log message string
    :param details: (dict) Extra details to show {'label': 'value'}
    :param pad: (bool) Whether the extra detail lines should be padded
    '''
    formatted_tag = click.style(tag, fg=color, bold=True)
    print(f'{start}{formatted_tag} {message}', end=end)

    if details:
        format_label = lambda text: click.style(text, fg='white', dim=True, bold=True)

        for label, msg in details.items():
            padding = len(tag) * ' ' + ' ' if pad else ''
            print(padding + format_label(label), msg)


def log_trace(*args, **kwargs):
    '''
    Log a trace message (see log())
    '''
    log('trace', 'white', *args, **kwargs)


def log_info(*args, **kwargs):
    '''
    Log an info message (see log())
    '''
    log('info', 'green', *args, **kwargs)


def log_warn(*args, **kwargs):
    '''
    Log a warning (see log())
    '''
    log('warn', 'yellow', *args, **kwargs)


def log_err(*args, **kwargs):
    '''
    Log an error (see log())
    '''
    log('err', 'red', *args, **kwargs)
