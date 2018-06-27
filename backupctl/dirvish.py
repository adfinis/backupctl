#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

import jinja2
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class Dirvish:
    """Create dirvish configuration and handle dirvish server triggers.

    :ivar sqlalchemy.engine.base.Engine engine: SQLAlchemy engine.

    :raises sqlalchemy.exc.ArgumentError: Raised when an invalid or conflicting
                                          function argument is supplied.
    :raises sqlalchemy.exc.OperationalError: Wraps a DB-API OperationalError.
    """

    def __init__(self, engine):
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
        self._engine = engine
        Base.metadata.create_all(engine)

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
