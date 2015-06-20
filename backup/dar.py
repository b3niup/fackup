import glob
import logging

from datetime import datetime
from subprocess import Popen, PIPE

from backup.config import config, get_server_config
from backup.exceptions import DarError, \
    ServerConfigNotFound, BasicConfigNotFound

class Dar:
    def __init__(self, server):
        self.server = server
        self._setup_config()

        self.source_type = self.config['server'].get('source_type')
        self.config['default'] = config[self.source_type].get('backup')

        self.binary = self._get_cfg('bin')
        self.params = self._get_cfg('params', '')
        self.config_file = self._get_cfg('config')
        self.max_diff = int(self._get_cfg('max_diff'))

        self.source = "{base}/{d}/rsync".format(
            base=self.config['default']['dir'],
            d=self.config['server'].get('dir', self.server))
        self.dest = "{base}/{d}/dar".format(
            base=self.config['default']['dir'],
            d=self.config['server'].get('dir', self.server))

    def _setup_config(self):
        self.config = {
            'global': config['general'].get('dar'),
            'server': get_server_config(self.server)
        }

        if self.config['global'] is None:
            err_msg = "Global config not found."
            logging.error(err_msg)
            raise BasicConfigNotFound(err_msg)

        if self.config['server'] is None:
            err_msg = '%s is not defined in configuration file!' % self.server
            logging.error(err_msg)
            raise ServerConfigNotFound(err_msg)

    def _get_cfg(self, param, default=None):
        for key in ['server', 'default', 'global']:
            val = self.config[key].get(param)
            if val is not None:
                break
        if val is None:
            val = default
        return val

    def _get_cfg_all(self, param):
        vals = []
        for key in self.config.keys():
            vals += self.config[key].get(param, [])
        return vals

    def _get_ref(self):
        backups = glob.glob('{0}/*.dar.*'.format(self.dest))
        backups.sort(reverse=True)

        ref = None
        diff_count = 0

        for backup in backups:
            if backup.find('_full.dar') != -1:
                break
            diff_count += 1

        if diff_count < self.max_diff and backups:
            ref = backups[0]
            stop = ref.rfind('.dar')
            ref = ref[:stop]
            logging.info("Found {count} differential backups, \
                         creating another one, based on {ref}".format(
                             count=diff_count, ref=ref[ref.rfind('/'):]))
        else:
            if backups:
                logging.info("Found {count} differential backups, \
                             creating full one.".format(count=diff_count))
            else:
                logging.info("No backups found, creating full one.")
        return ref

    def get_cmd(self):
        " Returns cmd ready to run as subprocess.Popen arg "

        cmd = [self.binary, self.params]
        ref = self._get_ref()
        date = datetime.now().strftime('%Y%m%d')

        if ref:
            t = 'diff'
        else:
            t = 'full'

        filename = '{dest}/{date}_{t}'.format(dest=self.dest,
                                                 date=date,
                                                 t=t)
        cmd += ['-c', filename]

        if ref:
            cmd += ['-A', ref]

        if self.config_file:
            cmd += ['-B', self.config_file]

        cmd += ['-R', self.source]

        return cmd

    def run(self, full=False):
        cmd = self.get_cmd()
        logging.info(" ".join(cmd))

        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        logging.debug(stdout)
        if stderr:
            logging.error(stderr)
            raise DarError(stderr)
