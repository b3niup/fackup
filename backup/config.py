import os
import yaml

from backup.exceptions import ConfigNotFound

DEFAULT_CONFIG_PATHS = [
    './backup.yml',
    '~/.backup.yml',
    '/etc/backup.yml',
]

config = None

def load_config(path=None):
    global config

    paths = DEFAULT_CONFIG_PATHS
    if path:
        paths.insert(0, path)

    for config_path in DEFAULT_CONFIG_PATHS:
        config_path = os.path.expanduser(config_path)
        if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
            with open(config_path, 'r') as f:
                config = yaml.load(f)
            break
    else:
        raise ConfigNotFound("Could not find {path}".format(
            path=path if path else "backup.yml"))

    return config

def get_server_config(hostname, source_type=None):
    if source_type is None:
        for t in ['local', 'remote']:
            server_config = get_server_config(hostname, t)
            if server_config is not None:
               break
    else:
        for i in range(len(config[source_type]['hosts'])):
            server_config = config[source_type]['hosts'][i]
            if server_config.get('hostname', '') == hostname:
                server_config['source_type'] = source_type
                break
            else:
                server_config = None
    return server_config

def get_hosts(source_type="all"):
    if source_type == "all":
        return get_hosts("local") + get_hosts("remote")
    else:
        hosts = []
        for host in config[source_type]['hosts']:
            hosts.append(host['hostname'])
        return hosts
