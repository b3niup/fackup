import glob

from datetime import datetime

from backup.cmd import BackupCommand


class Dar(BackupCommand):
    def __init__(self, server, force_full=False):
        super(Dar, self).__init__(server)

        self.force_full = force_full

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

    def _get_ref(self):
        ref = None
        diff_count = 0

        if self.force_full:
            self.logger.info("Forced full backup.")
            return None

        backups = glob.glob('{0}/*.dar'.format(self.dest))
        backups.sort(reverse=True)

        for backup in backups:
            if backup.find('_full.dar') != -1:
                break
            diff_count += 1

        if diff_count < self.max_diff and backups:
            ref = backups[0]
            stop = ref.rfind('.dar')
            stop = ref[:stop].rfind('.')
            ref = ref[:stop]
            self.logger.info("Found {count} differential backups, " \
                             "creating another one, based on {ref}".format(
                                 count=diff_count,
                                 ref=ref[ref.rfind('/'):]))
        else:
            if backups:
                self.logger.info("Found {count} differential backups, " \
                                 "creating full one.".format(count=diff_count))
            else:
                self.logger.info("No backups found, creating full one.")
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

