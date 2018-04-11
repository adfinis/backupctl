#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys

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
        "-c", "--server",
        required=False,
        default=None,
        help="""\
        Hostname and dirvish vault name of the server to backup.
        Use a fully qualified domain name for that.
        """,
    )
    parser.add_argument(
        "--dirvish-client",
        required=False,
        default=None,
        help="""\
        Specify a client ip or fqdn to back up. Needed if different from
        option client.
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
        Quota of a customer or a server. Size can be written human readable as
        MB, GB and so on.
        """,
    )
    args = parser.parse_args()

    if args.command == 'new':
        new(args.customer, args.server, args.size)
    elif args.command == 'resize':
        resize(args.customer, args.server, args.size)
    elif args.command == 'remove':
        remove(args.customer, args.server)
    elif args.command == 'log':
        log()
    else:
        sys.exit(1)
    sys.exit(0)


def new(customer, server, size):
    """Create a new customer or a new server.

    :param string customer: Customer name.
    :param string server:   Server hostname and dirvish vault name.
    :param string size:     Quota for this customer or server.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if not server and not size:
        LOG.error('If no server is given, a size is required')
        sys.exit(1)
    if not server:
        new_customer(customer, size)
    else:
        new_server(customer, server, size)
    sys.exit(0)


def resize(customer, server, size):
    """Resize an existing customer or server.

    :param string customer: Customer name.
    :param string server:   Server hostname and dirvish vault name.
    :param string size:     Quota for this customer or server.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if not size:
        LOG.error('A size is required')
        sys.exit(1)
    if not server:
        resize_customer(customer, size)
    else:
        resize_server(customer, server, size)
    sys.exit(0)


def remove(customer, server):
    """Remove a customer or server.

    :param string customer: Customer name.
    :param string server:   Server hostname and dirvish vault name.
    """
    if not customer:
        LOG.error('Customer is needed')
        sys.exit(1)
    if not server:
        remove_customer(customer)
    else:
        remove_server(customer, server)
    sys.exit(0)


def log():
    """Manage the command log.
    """
    sys.exit(0)


if __name__ == '__main__':
    main()
