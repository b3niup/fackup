import logging
import sys

from fackup.config import config


def setup_logging(verbose, quiet, logger=None):
    if not logger:
        logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter('[%(asctime)s] [%(process)d] ' \
                            '%(levelname)-5s (%(name)s) %(message)s',
                            '%Y-%m-%d %H:%M:%S')

    logfile = config['general']['logging'].get('file')
    if logfile:
        logfile_level = config['general']['logging'].get('level', 'info')
        logfile_level = logfile_level.lower()

        f = logging.FileHandler(logfile)
        if logfile_level == "error":
            f.setLevel(logging.ERROR)
        elif logfile_level == "debug":
            f.setLevel(logging.DEBUG)
        else:
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

    if not quiet and not verbose:
        stderr = logging.StreamHandler()
        stderr.setLevel(logging.ERROR)
        stderr.setFormatter(fmt)
        logger.addHandler(stderr)
