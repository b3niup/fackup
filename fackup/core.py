import logging

from multiprocessing import Pool

from fackup.args import parse_args
from fackup.config import config_load, config_verify, get_hosts

args = parse_args()
config = config_load(args.config)

from fackup.log import setup_logging

setup_logging(args.verbose, args.quiet)

from fackup.dar import Dar
from fackup.rsync import Rsync


def process(server):
    logger = logging.getLogger(server)
    logger.debug("Starting backup.")
    r = Rsync(server, args.dry_run)
    d = Dar(server, args.full, args.dry_run)
    r.run()
    d.run()
    logger.debug("Backup done.")


def main():
    config_verify(config)

    if args.host:
        hosts = args.host
    else:
        hosts = get_hosts(args.source_group)

    logging.info("Starting backup for {hosts}.".format(hosts=", ".join(hosts)))

    p = Pool(int(config['general'].get('process_pool', 5)))
    p.map_async(process, hosts)
    p.close()
    p.join()

    logging.info("Backup done.")

