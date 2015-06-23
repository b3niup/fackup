import logging
import os

from subprocess import Popen, PIPE

import backup.exceptions
from backup.config import config, get_server_config

class BackupCommand(object):
    def __init__(self, server):
        self.server = server
        self.logger = logging.getLogger(server)

        self._setup_config()

        self.source_type = self.config['server'].get('source_type')
        self.config['default'] = config[self.source_type].get('backup')

    def _setup_config(self):
        self.config = {
            'global': config['general'].get(self.__class__.__name__.lower()),
            'server': get_server_config(self.server)
        }

        if self.config['global'] is None:
            err_msg = "Global config not found."
            self.logger.error(err_msg)
            raise backup.exceptions.BasicConfigNotFound(err_msg)

        if self.config['server'] is None:
            err_msg = 'Server is not defined in configuration file!'
            self.logger.error(err_msg)
            raise backup.exceptions.ServerConfigNotFound(err_msg)

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

    def get_cmd(self):
        " Should be overwritten by child class. "
        pass
    def run(self):
        if not os.path.isdir(self.dest):
            try:
                os.makedirs(self.dest, 0o700)
            except Exception as e:
                self.logger.exception(e)
                raise

        cmd = self.get_cmd()
        self.logger.debug(" ".join(cmd))

        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        if stdout:
            self.logger.debug(stdout.decode())
        if stderr:
            self.logger.error(stderr.decode())
            error = getattr(backup.exceptions,
                            '{0}Error'.format(self.__class__.__name__))
            raise error(stderr)
