from backup.cmd import BackupCommand


class Rsync(BackupCommand):
    def __init__(self, server, dry_run=False):
        super(Rsync, self).__init__(server)

        self.dry_run = dry_run

        self.binary = self._get_cfg('bin')
        self.params = self._get_cfg('params', '').split()
        self.protocol = self._get_cfg('protocol')
        self.user = self._get_cfg('user')
        self.port = self._get_cfg('port')
        self.ssh_key = self._get_cfg('ssh_key')
        self.rsync_path = self._get_cfg('rsync_path')
        self.source = self._get_source()
        self.exclude = self._get_excludes(self.source)
        self.dest = '{base}/{d}/rsync'.format(
            base=self.config['default']['dir'],
            d=self.config['server'].get('dir', self.server))

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

        source = self.source

        cmd = [self.binary]
        cmd += self.params

        if self.source_type == 'remote':
            protocol = self.protocol
            if self.port:
                protocol += ' -p {0}'.format(self.port)
            if self.ssh_key:
                protocol += ' -i {0}'.format(self.ssh_key)

            cmd += ['-e', '{0}'.format(protocol)]

            if self.rsync_path:
                cmd.append('--rsync-path={0}'.format(self.rsync_path))

            first = source[0]
            source.remove(first)
            cmd.append('{0}@{1}{2}'.format(self.user, self.server, first))

        cmd += source

        if self.exclude:
            for item in self.exclude:
                cmd.append('--exclude={0}'.format(item))

        cmd.append(self.dest)

        return cmd
