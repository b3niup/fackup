import logging

from subprocess import Popen, PIPE

from backup.config import config, get_server_config
from backup.exceptions import RsyncError, \
    ServerConfigNotFound, BasicConfigNotFound

class Rsync:
    def __init__(self, server):
        self.server = server
        self.config = {
            'global': config['general'].get('rsync'),
            'server': get_server_config(server)
        }

        if self.config['global'] is None:
            err_msg = "Global config not found."
            logging.error(err_msg)
            raise BasicConfigNotFound(err_msg)

        if self.config['server'] is None:
            err_msg = '%s is not defined in configuration file!' % self.server
            logging.error(err_msg)
            raise ServerConfigNotFound(err_msg)

        self.source_type = self.config['server'].get('source_type')
        self.config['default'] = config[self.source_type].get('backup')

        self.binary = self._get_cfg('bin')
        self.params = self._get_cfg('params')
        self.protocol = self._get_cfg('protocol')
        self.user = self._get_cfg('user')
        self.port = self._get_cfg('port')
        self.ssh_key = self._get_cfg('ssh_key')
        self.source = self._get_source()
        self.exclude = self._get_excludes(self.source)
        self.dest = "{base}/{d}/rsync".format(
            base=self.config['default']['dir'],
            d=self.config['server'].get('dir', self.server))

    def _get_cfg(self, param):
        for key in ['server', 'default', 'global']:
            val = self.config[key].get(param)
            if val is not None:
                break
        return val

    def _get_cfg_all(self, param):
        vals = []
        for key in self.config.keys():
            vals += self.config[key].get(param, [])
        return vals

    def _get_source(self):
        source = []

        paths = self._get_cfg_all('paths')

        excludes = self.config['server'].get('exclude', [])

        for path in paths:
            if path in excludes:
                continue

            if self.source_type == 'remote':
                path = ':%s' % path
            source.append(path)
        return source

    def _get_excludes(self, sources=None):
        if not sources:
            sources = self._get_source()

        paths = self._get_cfg_all('exclude')

        excludes = []

        for exclude in paths:
            # convert absolute to rsync (relative) excludes
            if exclude.startswith('/'):
                match_len = len(exclude)
                match = None
                for source in sources:
                    if self.source_type == 'remote':
                        source = source[1:]

                    # find shortest matching source to be most precise with
                    # exclude
                    if exclude.startswith(source) and len(source) < match_len:
                        match = source
                        match_len = len(match)
                if match:
                    slash = match.rfind('/')
                    match = match[:slash]
                    excludes.append(exclude[len(match)+1:])
            # already relative exclude
            else:
                excludes.append(exclude)
        return excludes

    def get_cmd(self):
        " Returns cmd ready to run as subprocess.Popen arg "

        cmd = [self.binary, self.params]

        if self.source_type == 'remote':
            protocol = self.protocol
            if self.port:
                protocol += ' -p {0}'.format(self.port)
            if self.ssh_key:
                protocol += ' -i {0}'.format(self.ssh_key)

            cmd += ['-e', '"%s"' % protocol]
            cmd.append("{0}@{1}".format(self.user, self.server))

        cmd.append(" ".join(self.source))

        if self.exclude:
            for item in self.exclude:
                cmd.append("--exclude={0}".format(item))

        cmd.append(self.dest)

        return cmd

    def run(self):
        cmd = self.get_cmd()
        logging.info(" ".join(cmd))

        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        logging.debug(stdout)
        if stderr:
            logging.error(stderr)
            raise RsyncError(stderr)
