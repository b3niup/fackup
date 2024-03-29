import logging
import os
import yaml

import fackup.exceptions

DEFAULT_CONFIG_PATHS = [
    './fackup.yml',
    '~/.fackup.yml',
    '/etc/fackup.yml',
]

config = None

def config_get(path):
    config = None
    config_path = os.path.expanduser(path)
    if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    return config

def config_load(path=None):
    global config

    paths = DEFAULT_CONFIG_PATHS
    if path:
        paths.insert(0, path)

    for config_path in DEFAULT_CONFIG_PATHS:
        config = config_get(config_path)
        if config is not None:
            break
    else:
        raise fackup.exceptions.ConfigNotFound('Could not find {path}'.format(
            path=path if path else 'fackup.yml'))

    return config

def config_verify(config):
    if config is None:
        raise fackup.exceptions.ConfigNotFound('Config not found.')

    general = config.get('general')
    if general is None:
        err_msg = 'General config not found.'
        raise fackup.exceptions.BasicConfigNotFound(err_msg)

    for cmd in ['rsync', 'dar']:
        cmd_conf = general.get(cmd)
        if cmd_conf is None:
            err_msg = '{0} command configuration not found.'.format(cmd)
            logging.error(err_msg)
            raise fackup.exceptions.CommandConfigNotFound(err_msg)

        cmd_path = cmd_conf.get('bin')
        if cmd_path is None:
            err_msg = '{0} binary path is not defined in configuration!'
            err_msg = err_msg.format(cmd)
            logging.error(err_msg)
            raise fackup.exceptions.CommandNotFound(err_msg)

        if not os.path.isfile(cmd_path):
            err_msg = '{0} does not exist! Are you sure that {1} is installed?'
            err_msg = err_msg.format(cmd_path, cmd)
            logging.error(err_msg)
            raise fackup.exceptions.CommandNotFound(err_msg)

        if not os.access(cmd_path, os.X_OK):
            err_msg = '{0} is not executable!'.format(cmd_path)
            logging.error(err_msg)
            raise fackup.exceptions.CommandNotFound(err_msg)

def get_server_groups():
    return list(config.get('groups', {}).keys())

def get_server_config(hostname, source_group=None):
    if source_group is None:
        for g in get_server_groups():
            server_config = get_server_config(hostname, g)
            if server_config is not None:
               break
    else:
        for i in range(len(config['groups'][source_group]['hosts'])):
            server_config = config['groups'][source_group]['hosts'][i]
            if server_config.get('hostname', '') == hostname:
                server_config['source_group'] = source_group
                break
            else:
                server_config = None
    return server_config

def get_hosts(source_group="all"):
    hosts = []
    if source_group == "all":
        groups = get_server_groups()
    elif ',' in source_group:
        groups = source_group.split(',')
    else:
        groups = [source_group, ]

    for group in groups:
        if group in config.get('groups', {}):
            for host in config['groups'][group].get('hosts', []):
                hosts.append(host['hostname'])
    return hosts
