class CommandError(Exception):
    """
    Exception class indicating a problem while executing a stapler command.
    """
    pass

OPTIONS = None # optparse options


def main(arguments=None):
    from . import stapler
    stapler.main(arguments)
