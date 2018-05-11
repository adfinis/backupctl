#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sqlite3

import jinja2

logger = logging.getLogger(__name__)


class Dirvish:
    """Create dirvish configuration and handle dirvish server triggers.

    :ivar string dbpath: Path to the backupctl database.

    :raises sqlite3.OperationalError: if couldn't open the database.
    """

    def __init__(self, dbpath):
        self._excludes_default = [
            '/dev/*',
            '/tmp/*',
            '/var/tmp/*',
            '/run/*',
            '/var/run/*',
            '/proc/*',
            '/sys/*',
            '*.bak',
            '/var/cache/man/*',
            '/var/cache/apt/archives/*',
            '/var/cache/yum/*',
            'lost+found/',
            '*~',
        ]
        self._path = None
        self._conn = None

        self._path = dbpath
        self._conn = sqlite3.connect(self._path)
        logger.debug(
            "Opened database {0} successfully".format(self._path)
        )
        self._conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS servers
                (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    name          TEXT                              NOT NULL,
                    vault         TEXT                              NOT NULL,
                    backupserver  TEXT                              NOT NULL,
                    enabled       INTEGER                           NOT NULL
                )
            ;'''
        )
        self._conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS backups
                (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    server_id     INTEGER,
                    start         DATETIME,
                    end           DATETIME,
                    status        TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(id)
                )
            ;'''
        )
        self._conn.commit()

    def create_config(self, root, customer, vault, client, excludes=None):
        """Create default dirvish configuration.

        :param string root:     Backup root path.
        :param string customer: Customer name.
        :param string vault:    Dirvish vault.
        :param string client:   Client fqdn or IP address.

        :returns: True if the dirvish configuration was written, else False.
        :rtype: bool
        """
        root_dir = os.path.dirname(os.path.abspath(__file__))
        config_path_j2 = os.path.join(root_dir, 'dirvish.conf.j2')
        config_root = os.path.join(
            root,
            customer,
            vault,
            'dirvish',
        )
        config_path = os.path.join(
            config_root,
            'default.conf',
        )
        if excludes is None:
            excludes = self._excludes_default
        try:
            with open(config_path_j2, 'r') as conf_jinja:
                os.makedirs(config_root, mode=0o755, exist_ok=True)
                with open(config_path, 'w') as conf:
                    content = conf_jinja.read()
                    content_rendered = jinja2.Environment().from_string(
                        content,
                    ).render(
                        client=client,
                        excludes=excludes,
                    )
                    conf.write(
                        content_rendered,
                    )
        except FileNotFoundError as e:
            logger.error("couldn't open configuration file {0}: {1}".format(
                config_path,
                e,
            ))
        print(
            'You should now edit the dirvish configuration and run an '
            'initial backup.\n'
            '$EDITOR {0}/{1}/{2}/dirvish/default.conf\n'
            'dirvish --vault {1}/{2} --init\n'.format(
                root,
                customer,
                vault,
            )
        )
        return True

    def server_add(self, name, vault, backupserver):
        """Add a server to the list of servers to backup if it doesn't exist.

        :param string name:         Server name.
        :param string vault:        Dirvish vault name.
        :param string backupserver: Name of the backup server.

        :returns: 1 if a server was added, 0 if the server existed.
        :rtype: int
        """
        cur = self._conn.cursor()
        cur.execute(
            '''
            SELECT COUNT(*) FROM servers
            WHERE name=? AND vault=? AND backupserver=?
            ;''', (
                name,
                vault,
                backupserver,
            )
        )
        try:
            count = cur.fetchall()[0][0]
        except KeyError as e:
            logger.warn(
                "Couldn't get the count, assume no server is existing!"
            )
            count = 0

        if count == 0:
            self._conn.execute(
                '''
                INSERT INTO servers
                    (
                        name,
                        vault,
                        backupserver,
                        enabled
                    )
                VALUES
                    (
                        ?,
                        ?,
                        ?,
                        1
                    )
                ;''', (
                    name,
                    vault,
                    backupserver,
                )
            )
        else:
            cur = self._conn.cursor()
            cur.execute(
                '''
                SELECT COUNT(*) FROM servers
                WHERE name=? AND vault=? AND backupserver=? AND enabled=0
                ;''', (
                    name,
                    vault,
                    backupserver,
                )
            )
            try:
                count = cur.fetchall()[0][0]
            except KeyError as e:
                logger.warn(
                    "Couldn't get the count, assume no server is existing!"
                )
                count = 0
            if count == 1:
                self._conn.execute(
                    '''
                    UPDATE servers
                    SET enabled=1
                    WHERE name=? AND vault=? AND backupserver=?
                    ;''', (
                        name,
                        vault,
                        backupserver,
                    )
                )
            else:
                return 0

        self._conn.commit()
        return 1

    def server_disable(self, name, vault, backupserver):
        """Disable a server in the list of servers to backup.

        :param string name:         Server name.
        :param string vault:        Dirvish vault name.
        :param string backupserver: Name of the backup server.
        """
        self._conn.execute(
            '''
            UPDATE servers
            SET enabled=0
            WHERE name=? AND vault=? AND backupserver=?
            ;''', (
                name,
                vault,
                backupserver,
            )
        )
        self._conn.commit()
        return True
