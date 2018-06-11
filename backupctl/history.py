#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sqlite3

logger = logging.getLogger(__name__)


class History:
    """Store and show history of commands done with the backupctl tool.

    :ivar string dbpath: Path to the backupctl database. The directory must
                         exist.

    :raises sqlite3.OperationalError: if couldn't open the database.
    """

    def __init__(self, dbpath):
        self._path = None
        self._conn = None

        self._path = dbpath
        self._conn = sqlite3.connect(self._path)
        logger.debug(
            "Opened database {0} successfully".format(self._path)
        )
        self._conn.execute(
            '''CREATE TABLE IF NOT EXISTS history
                (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT   NOT NULL,
                    datetime    REAL                                NOT NULL,
                    command     TEXT                                NOT NULL,
                    customer    TEXT                                NOT NULL,
                    vault       TEXT,
                    size        TEXT
                )
            ;'''
        )
        self._conn.commit()

    def add(self, customer, command, vault=None, size=None):
        """Add an entry to the history.

        :param string customer: Customer name.
        :param string command:  Used subcommand, e.g. create or resize.
        :param string vault:    Vault name or server hostname.
        :param string size:     Quota size.

        :returns: True
        :rtype: bool

        :raises sqlite3.OperationalError: if database schematic is wrong or
        database is not writtable.
        """
        self._conn.execute(
            '''INSERT INTO history
                (
                    datetime,
                    command,
                    customer,
                    vault,
                    size
                )
            VALUES
                (
                    julianday('now'),
                    ?,
                    ?,
                    ?,
                    ?
                )
            ;''', (
                command,
                customer,
                vault,
                size,
            )
        )
        self._conn.commit()
        return True

    def show(self, count=20):
        """Show the history.

        :param int customer:    Number of entries to show.

        :returns: A list of entries.
        :rtype: `list` of `string`

        :raises sqlite3.OperationalError: if database schematic is wrong or
        database is not readable.
        """
        history_list = []
        cur = self._conn.cursor()
        cur.execute(
            '''SELECT
                date(datetime),
                time(datetime),
                command,
                customer,
                vault,
                size
            FROM history
            ORDER BY datetime
            LIMIT ?''',
            (count,)
        )
        for row in cur:
            dt = '{0}T{1}'.format(row[0], row[1])
            command = row[2]
            customer = ' customer "{0}"'.format(row[3]) if row[3] else ''
            vault = ' vault "{0}"'.format(row[4]) if row[4] else ''
            size = ' with size {0}'.format(row[5]) if row[5] else ''
            history_list.append(
                '{0} - {1}{2}{3}{4}'.format(
                    dt,
                    command,
                    customer,
                    vault,
                    size,
                )
            )
        return history_list
