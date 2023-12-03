# fackup
File backup tool using rsync and dar.

**Note that this is still alpha software.**

## Featuring:

* Local and remote system backup
* Multiprocessing
* Compression
* Incremental backup
* ...and more!

## How?

Fackup rsyncs defined directories into local filesystem 
and creates full or incremental dar archives depending on configuration.

## Requirements

* [Python 3](http://python.org)
* [PyYAML](http://pyyaml.org/wiki/PyYAML)
* [rsync](https://rsync.samba.org)
* [dar - Disk ARchive](http://dar.linux.free.fr/)

# Installation

### Arch Linux
[Arch Linux](https://www.archlinux.org/) users can simply install fackup from [AUR](https://aur.archlinux.org/packages/fackup/).

### Other distributions

Please make sure that requirements are installed before using fackup.  
Both [rsync](https://rsync.samba.org) and [dar](http://dar.linux.free.fr/) 
should be available in your distro repository. 

Then, you can install fackup from pip:
```
pip3 install fackup
```

or get the source and run:

```
python3 setup.py install
```

Then setup your configuration as explained below.


# Configuration

Fackup will attempt to read `./fackup.conf`, `~/.fackup.conf` and `/etc/fackup.conf` in that order.

Simple example:
```yaml
general:
  logging:
    file: /root/fackup.log                  # log file

  rsync:
    bin: /usr/bin/rsync                     # local rsync path
    params: "-XRa --stats --delete"         # rsync additional parameters
    protocol: ssh                           # default rsync protocol

  dar:
    bin: /usr/bin/dar                       # local dar path


groups:
	local:
	  backup:                                   # general config for local hosts
		dir: /backup/local                      # base local backup dir

	  hosts:
		- hostname: desktop
		  paths:
			- /home/xxx/Books
			- /home/xxx/Docs
			- /home/xxx/dotfiles
			- /home/xxx/tools
		  exclude:
			- /home/xxx/Docs/School

	remote:
	  backup:                                   # general config for remote hosts
		dir: /backup/remote                     # base local backup dir
		paths:
		  - /etc                                # default paths to include in backup
		  - /root
		  - /var

	  hosts:
		- hostname: host1.example.com
		- hostname: host2.example.com
		- hostname: host3.example.com

```

You can find more complex configuration example in *fackup.yml.example* file.

# Usage

After setting up configuration all you need to do is to run `fackup` every once in a while.


```
usage: fackup [-h] [--verbose] [--quiet] [--config CONFIG]
              [--type {local,remote,all}] [--host HOST] [--full]
              [--dry-run]

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v
  --quiet, -q
  --config CONFIG, -c CONFIG
  --type {local,remote,all}, -t {local,remote,all}
                        Backup all servers of specified type.
  --host HOST, -H HOST  Backup only specified host(s).
  --full                Force dar to create full backup.
  --dry-run, -n         Perform a trial run with no changes made
```

## Local filesystem structure
Fackup stores locally both fresh rsync'ed files and dar archive snapshots.

With setup based on example configuration file local filesystem structure will be similar to following:
```
/backup
├── local
│   └── desktop
│       ├── dar
│       └── rsync
└── remote
    ├── example
    │   ├── host2
    │   │   ├── dar
    │   │   └── rsync
    │   ├── host3
    │   │   ├── dar
    │   │   └── rsync
    │   └── host4
    │       ├── dar
    │       └── rsync
    └── host1
        ├── dar
        └── rsync
```


## Restoration

**Fackup** in current version **does not implement any restoration mechanism**.

Because rsync directory always contains latest backup you can use any method you like to restore files to their original location.

To restore data from dar archives you can use steps described in [DAR Tutorial] (http://dar.linux.free.fr/doc/Tutorial.html).


# Tips

## rsync with sudo

As mentioned in fackup.yml.example I decided to create special user on remote systems
with backup-dedicated ssh key. 
To have full access to remote filesystems I'm allowing backup user to run rsync server with sudo.


Sample ansible role excerpt for user creation and sudoers setup:
```yaml
- name: Create backup user
  user: name=backup shell=/bin/bash 
  tags:
    - backup

- name: Upload rsync backup key
  authorized_key: user=backup key="{{ item }}"  #"
  with_items: backup['rsync']['keys']
  tags:
    - backup

- name: Allow backup user to run rsync server as root
  lineinfile: dest=/etc/sudoers state=present regexp='^backup'
              line='backup ALL= NOPASSWD:/usr/bin/rsync'
              validate='visudo -cf %s'
  tags:
    - backup
    - sudoers

- name: Allow backup user to run rsync without tty
  lineinfile: dest=/etc/sudoers state=present regexp='^Defaults:backup'
              line='Defaults:backup !requiretty'
              validate='visudo -cf %s'
  tags:
    - backup
    - sudoers
```

## TODO
* Rewrite config-related functions.
* Add tests.
* Add backup validation.
* Add full backup restoration(?)

