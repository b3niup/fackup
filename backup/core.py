#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import logging

from multiprocessing import Pool

from backup.config import load_config, get_hosts
from backup.log import setup_logging

config = load_config()

from backup.dar import Dar
from backup.rsync import Rsync



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--quiet', '-q', action='count')
    parser.add_argument('--type', '-t', choices=['local', 'remote', 'all'],
                        action='store', default='all', dest='source_type',
                        help="Backup all servers of specified type.")
    parser.add_argument('--host', '-H', action="append",
                        help="Backup only specified host(s).")
    parser.add_argument('--full', action='store_true',
                        help="Force dar to create full backup.")
    args = parser.parse_args()
    return args


def process(server):
    logging.info("Starting backup.", extra={'server': server})
    r = Rsync(server)
    d = Dar(server)
    r.run()
    d.run()
    logging.info("Backup done.", extra={'server': server})


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args.verbose, args.quiet)

    hosts = get_hosts(args.source_type)

    logging.info("Starting backup for {hosts}.".format(hosts=", ".join(hosts)),
                 extra={'server': ''})

    p = Pool(int(config['general'].get('process_pool', 5)))
    p.map_async(process, hosts)
    p.close()
    p.join()

    logging.info("Backup done.", extra={'server', ''})

