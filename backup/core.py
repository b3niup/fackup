import logging

from multiprocessing import Pool

from backup.args import parse_args
from backup.config import load_config, get_hosts

args = parse_args()
config = load_config(args.config)

from backup.log import setup_logging

setup_logging(args.verbose, args.quiet)

from backup.dar import Dar
from backup.rsync import Rsync


def process(server):
    logging.info("Starting backup.", extra={'server': server})
    r = Rsync(server)
    d = Dar(server)
    r.run()
    d.run()
    log.debug("[{server}] Backup done.".format(**locals))


def main():
    if args.host:
        hosts = args.host
    else:
        hosts = get_hosts(args.source_type)

    logging.info("Starting backup for {hosts}.".format(hosts=", ".join(hosts)),
                 extra={'server': ''})

    p = Pool(int(config['general'].get('process_pool', 5)))
    p.map_async(process, hosts)
    p.close()
    p.join()

    logging.info("Backup done.")

