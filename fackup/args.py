import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--quiet', '-q', action='count')
    parser.add_argument('--config', '-c', action='store')
    parser.add_argument('--group', '-g', action='store',
                        default='all', dest='source_group',
                        help="Backup all servers of specified group/groups.")
    parser.add_argument('--host', '-H', action="append",
                        help="Backup only specified host(s).")
    parser.add_argument('--full', action='store_true',
                        help="Force dar to create full backup.")
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help="Perform a trial run with no changes made")
    args = parser.parse_args()
    return args
