import logging

from backup.config import config


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                            '%Y-%m-%d %H:%M:%S')

    stderr = logging.StreamHandler()
    stderr.setLevel(logging.ERROR)
    stderr.setFormatter(fmt)

    f = logging.FileHandler(config['general']['logging']['file'])
    f.setLevel(logging.INFO)
    f.setFormatter(fmt)

    logger.addHandler(stderr)
    logger.addHandler(f)
