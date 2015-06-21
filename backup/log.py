import logging
import sys

from backup.config import config


def setup_logging(verbose, quiet):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter('%(asctime)s %(levelname)-8s \
                            %(server)s %(process)d %(message)s',
                            '%Y-%m-%d %H:%M:%S')

    f = logging.FileHandler(config['general']['logging']['file'])
    f.setLevel(logging.INFO)
    f.setFormatter(fmt)
    logger.addHandler(f)

    if verbose:
        stdout = logging.StreamHandler(sys.stdout)
        if verbose >= 2:
            stdout.setLevel(logging.DEBUG)
        else:
            stdout.setLevel(logging.INFO)
        stdout.setFormatter(fmt)
        logger.addHandler(stdout)

    if not quiet:
        stderr = logging.StreamHandler()
        stderr.setLevel(logging.ERROR)
        stderr.setFormatter(fmt)
        logger.addHandler(stderr)
