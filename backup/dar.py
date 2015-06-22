import glob

from datetime import datetime
from subprocess import Popen, PIPE

from backup.config import config, get_server_config
from backup.exceptions import DarError, \
    ServerConfigNotFound, BasicConfigNotFound

class Dar:
    def __init__(self, server, force_full=False):
        self.server = server
        self._setup_config()
        self.force_full=force_full

        self.log_extra = {'server': server}

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
            err_msg = "[{0}] Global config not found.".format(self.server)
            self.logger.error(err_msg)
            raise BasicConfigNotFound(err_msg)

        if self.config['server'] is None:
            err_msg = '[{0}] Server is not defined in configuration file!'.format(self.server)
            self.logger.error(err_msg)
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
        ref = None
        diff_count = 0

        if self.force_full:
            return None

        backups = glob.glob('{0}/*.dar.*'.format(self.dest))
        backups.sort(reverse=True)

        for backup in backups:
            if backup.find('_full.dar') != -1:
                break
            diff_count += 1

        if diff_count < self.max_diff and backups:
            ref = backups[0]
            stop = ref.rfind('.dar')
            ref = ref[:stop]
            self.logger.info("[{server}] Found {count} differential backups," \
                         "creating another one, based on {ref}".format(
                             server=self.server,
                             count=diff_count,
                             ref=ref[ref.rfind('/'):]))
        else:
            if backups:
                self.logger.info("[{server}] Found {count} differential " \
                                 "backups, creating full one.".format(
                                     server=self.server,
                                     count=diff_count))
            else:
                self.logger.info("[{server}] No backups found, " \
                                 "creating full one.".format(
                                     server=self.server))
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
        self.logger.debug("[{0}] {1}".format(self.server, " ".join(cmd)))

        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        self.logger.debug("[{0}] {1}".format(self.server, stdout))
        if stderr:
            self.logger.error("[{0}] {1}".format(self.server, stderr))
            raise DarError(stderr)
