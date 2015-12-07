class CommandError(Exception):
    """
    Exception class indicating a problem while executing a stapler command.
    """
    pass

OPTIONS = None # optparse options


def main():
    import stapler
    stapler.main()
