#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import logging
import os
import sys

import sqlalchemy
from xdg import BaseDirectory

from backupctl import zfs
from backupctl.dirvish import Dirvish
from backupctl.history import History

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.WARN)


def main():
    """Main function.
    Manage cli arguments and call the corresponding function per subcommand
    with the needed arguments.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
        Manage dirvish backups with an underlying zfs storage pool.
        """,
    )
    parser.add_argument(
        "command",
        help="""\
        All subcommands that modify zfs file system and dirvish configurations.
        See the manpage (man 8 backupctl) for more inforation.
        """,
    )
    parser.add_argument(
        "-v", "--vault",
        required=False,
        default=None,
        help="""\
        Dirvish vault name or server hostname to backup.
        Use a fully qualified domain name for that.
        """,
    )
    parser.add_argument(
        "--dirvish-client",
        required=False,
        default=None,
        help="""\
        Specify an ip address or fqdn for a dirvish vault to back up.
        Needed if different from option vault.
        """,
    )
    parser.add_argument(
        "-n", "--customer",
        required=False,
        default=None,
        help="""\
        Customer name. Used as a logical group of dirvish vaults.
        """,
    )
    parser.add_argument(
        "-s", "--size",
        required=False,
        default=None,
        help="""\
        Quota of a customer or a vault. Size can be written human readable as
        MB, GB and so on.
        """,
    )
    args = parser.parse_args()

    cfg = config()

    if not os.path.exists(os.path.dirname(cfg['database'].get('path'))):
        os.makedirs(os.path.dirname(cfg['database'].get('path')))

    try:
        engine = sqlalchemy.create_engine(cfg['database'].get('fullpath'))
        LOG.debug(
            "Opened database {0} successfully".format(
                cfg['database'].get('fullpath'),
            )
        )
    except sqlalchemy.exc.ArgumentError as e:
        LOG.error("Couldn't open database {0}. Exit now.".format(
            cfg['database'].get('fullpath'),
        ))
        sys.exit(1)
    except sqlalchemy.exc.OperationalError as e:
        LOG.error("Couldn't open database {0}. Exit now.".format(
            cfg['database'].get('fullpath'),
        ))
        sys.exit(1)

    hist = History(engine)
    dirvish = Dirvish(engine)

    if args.command == 'new':
        try:
            new(
                hist,
                dirvish,
                cfg['zfs']['pool'],
                cfg['zfs']['root'],
                args.customer,
                args.vault,
                args.size,
                args.dirvish_client,
            )
        except KeyError as e:
            LOG.error(
                "ZFS Pool and ZFS Root must be specified in the "
                "configuration file. Exit now."
            )
            sys.exit(1)
    elif args.command == 'resize':
        try:
            resize(
                hist,
                cfg['zfs']['pool'],
                args.customer,
                args.vault,
                args.size,
            )
        except KeyError as e:
            LOG.error(
                "ZFS Pool must be specified in the configuration file. "
                "Exit now."
            )
            sys.exit(1)
    elif args.command == 'remove':
        try:
            remove(
                hist,
                cfg['zfs']['pool'],
                args.customer,
                args.vault,
            )
        except KeyError as e:
            LOG.error(
                "ZFS Pool must be specified in the configuration file. "
                "Exit now."
            )
            sys.exit(1)
    elif args.command == 'log':
        history_show(hist)
    else:
        sys.exit(1)
    sys.exit(0)


def backup_start():
    """Add an entry to the database when a dirvish backup is started.

    This function should be triggered by dirvish pre-server.
    """
    cfg = config()
    if not os.path.exists(os.path.dirname(cfg['database'].get('path'))):
        os.makedirs(os.path.dirname(cfg['database'].get('path')))
    try:
        engine = sqlalchemy.create_engine(cfg['database'].get('fullpath'))
        LOG.debug(
            "Opened database {0} successfully".format(
                cfg['database'].get('fullpath'),
            )
        )
    except (
            sqlalchemy.exc.ArgumentError,
            sqlalchemy.exc.OperationalError,
    ) as e:
        LOG.error("Couldn't open database {0}. Exit now.".format(
            cfg['database'].get('fullpath'),
        ))
        sys.exit(1)
    dirvish = Dirvish(engine)
    dirvish.backup_start()


def backup_stop():
    """Add an entry to the database when a dirvish backup is stopped.

    This function should be triggered by dirvish post-server.
    """
    cfg = config()
    if not os.path.exists(os.path.dirname(cfg['database'].get('path'))):
        os.makedirs(os.path.dirname(cfg['database'].get('path')))
    try:
        engine = sqlalchemy.create_engine(cfg['database'].get('fullpath'))
        LOG.debug(
            "Opened database {0} successfully".format(
                cfg['database'].get('fullpath'),
            )
        )
    except sqlalchemy.exc.ArgumentError as e:
        LOG.error("Couldn't open database {0}. Exit now.".format(
            cfg['database'].get('fullpath'),
        ))
        sys.exit(1)
    except sqlalchemy.exc.OperationalError as e:
        LOG.error("Couldn't open database {0}. Exit now.".format(
            cfg['database'].get('fullpath'),
        ))
        sys.exit(1)
    dirvish = Dirvish(engine)
    dirvish.backup_stop()


def config():
    """Read the configuration files. If no configuration exists, write the
    default configuration to the directory ~/.config.

    :returns: Configuration object.
    :rtype: `configparser.ConfigParser`
    """
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(os.sep, 'etc', 'backupctl.ini'))
    cfg.read(os.path.join(BaseDirectory.xdg_config_home, 'backupctl.ini'))
    cfg.read('backupctl.ini')

    if not cfg.has_section('database'):
        cfg.add_section('database')
    if not cfg.has_option('database', 'type'):
        cfg['database']['type'] = 'sqlite'
    if not cfg.has_option('database', 'path'):
        cfg['database']['path'] = os.path.join(
            os.sep,
            'var',
            'lib',
            'backupctl',
            'backupctl.db',
        )
    if not cfg.has_option('database', 'fullpath'):
        cfg['database']['fullpath'] = '{0}:///{1}'.format(
            cfg['database'].get('type'),
            cfg['database'].get('path'),
        )
    return cfg


def new(hist, dirvish, pool, root, customer, vault=None, size=None,
        client=None):
    """Create a new customer or a new vault/server.

    :param history.History hist:    History database.
    :param dirvish.Dirvish dirvish: Dirvish object.
    :param string pool:             ZFS pool name.
    :param string root:             Backup root path.
    :param string customer:         Customer name.
    :param string vault:            Vault name or server hostname.
    :param string size:             Quota for this customer or vault.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if not vault and not size:
        LOG.error('If no vault is given, a size is required')
        sys.exit(1)
    if vault is not None:
        fs = os.path.join(pool, customer, vault)
        path = os.path.join(root, customer, vault)
    else:
        fs = os.path.join(pool, customer)
        path = os.path.join(root, customer)
    fs_status = zfs.new_filesystem(
        fs,
        path,
        size,
    )
    if fs_status:
        hist.add(customer, 'create', vault, size)
        if vault is not None:
            if client is None:
                client = vault
            dirvish.create_config(
                root,
                customer,
                vault,
                client,
            )
            hist.add(customer, 'config', vault)


def resize(hist, pool, customer, vault=None, size=None):
    """Resize an existing customer or vault.

    :param history.History hist:    History database.
    :param string pool:             ZFS pool name.
    :param string customer:         Customer name.
    :param string vault:            Vault name or server hostname.
    :param string size:             Quota for this customer or vault.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if not size:
        LOG.error('A size is required')
        sys.exit(1)
    if vault:
        fs = os.path.join(pool, customer, vault)
    else:
        fs = os.path.join(pool, customer)
    zfs.resize_filesystem(
        fs,
        size,
    )
    hist.add(customer, 'resize', vault, size)


def remove(hist, pool, customer, vault=None):
    """Remove a customer or vault.

    :param history.History hist:    History database.
    :param string pool:             ZFS pool name.
    :param string customer:         Customer name.
    :param string vault:            Vault name or server hostname.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if vault:
        fs = os.path.join(pool, customer, vault)
    else:
        fs = os.path.join(pool, customer)
    zfs.remove_filesystem(
        fs,
    )
    hist.add(customer, 'remove', vault)


def history_show(history):
    """Manage the command log.

    :param history.History history: History database.
    """
    for row in history.show():
        print(row)


if __name__ == '__main__':
    main()
