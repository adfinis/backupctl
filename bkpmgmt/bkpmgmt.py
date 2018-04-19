#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import configparser
import logging
import os
import sqlite3
import sys

from bkpmgmt import history

CONFIG_USER = '~/.config/bkpmgmt.ini'
CONFIG_SYSTEM = '/etc/bkpmgmt.ini'

CONFIG = configparser.ConfigParser()
CONFIG['database'] = {
    'path': '/var/lib/bkpmgmt.db',
}

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
        All subcommands that modify zfs volumes and dirvish configurations.
        See the manpage (man 8 bkpmgmt) for more inforation.
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

    global CONFIG
    try:
        CONFIG.read_file(open(os.path.expanduser(CONFIG_USER)))
    except FileNotFoundError as e:
        try:
            CONFIG.read_file(open(CONFIG_SYSTEM))
        except FileNotFoundError as e:
            with open(os.path.expanduser(CONFIG_USER), 'w') as configfile:
                CONFIG.write(configfile)
            LOG.warn('New configuration written to {0}'.format(CONFIG_USER))

    try:
        hist = history.History(CONFIG['database']['path'])
    except sqlite3.OperationalError as e:
        LOG.error("Couldn't open database {0}. Exit now.".format(
            CONFIG['database']['path'],
        ))
        sys.exit(1)

    if args.command == 'new':
        new(
            hist,
            args.customer,
            args.vault,
            args.size,
        )
    elif args.command == 'resize':
        resize(
            hist,
            args.customer,
            args.vault,
            args.size,
        )
    elif args.command == 'remove':
        remove(
            hist,
            args.customer,
            args.vault,
        )
    elif args.command == 'log':
        history_show(hist)
    else:
        sys.exit(1)
    sys.exit(0)


def new(customer, vault, size):
    """Create a new customer or a new vault/server.

    :param string customer: Customer name.
    :param string vault:    Vault name or server hostname.
    :param string size:     Quota for this customer or vault.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if not vault and not size:
        LOG.error('If no vault is given, a size is required')
        sys.exit(1)
    if not vault:
        new_customer(customer, size)
    else:
        new_vault(customer, vault, size)


def resize(customer, vault, size):
    """Resize an existing customer or vault.

    :param string customer: Customer name.
    :param string vault:    Vault name or server hostname.
    :param string size:     Quota for this customer or vault.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if not size:
        LOG.error('A size is required')
        sys.exit(1)
    if not vault:
        resize_customer(customer, size)
    else:
        resize_vault(customer, vault, size)


def remove(customer, vault):
    """Remove a customer or vault.

    :param string customer: Customer name.
    :param string vault:    Vault name or server hostname.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if not vault:
        remove_customer(customer)
    else:
        remove_vault(customer, vault)


def history_show(history):
    """Manage the command log.
    """
    for row in history.show():
        print(row)


if __name__ == '__main__':
    main()
