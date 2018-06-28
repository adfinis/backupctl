#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

import jinja2
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class MachineEntry(Base):
    __tablename__ = 'machines'

    id              = Column(Integer, primary_key=True)
    dirvish_client  = Column(String)
    dirvish_vault   = Column(String)
    dirvish_server  = Column(String)
    enabled         = Column(Boolean)

    def __repr__(self):
        return "<Entry(id='{0}')>".format(self.id)


class DirvishEntry(Base):
    __tablename__ = 'dirvish'

    id       = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    machine  = Column(Integer, ForeignKey(MachineEntry.id))
    trigger  = Column(String)
    status   = Column(Integer)

    def __repr__(self):
        return "<Entry(id='{0}')>".format(self.id)


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

    def create_machine(self, dirvish_server, dirvish_vault, dirvish_client):
        """Add a machine in the machines table if it doesn't exist.

        :param string dirvish_server:   Backup server (dirvish server).
        :param string dirvish_vault:    Backup vault (dirvish vault).
        :param string dirvish_client:   Backup client (machine to backup).

        :returns:   A server object.
        :rtype:     `dirvish.ServerEntry`
        """
        db_session = sessionmaker(bind=self._engine)
        session = db_session()

        machine = session.query(MachineEntry).filter_by(
            dirvish_client=dirvish_client,
            dirvish_vault=dirvish_vault,
            dirvish_server=dirvish_server,
        ).first()
        if not machine:
            machine = MachineEntry(
                dirvish_client=dirvish_client,
                dirvish_vault=dirvish_vault,
                dirvish_server=dirvish_server,
                enabled=True,
            )
            session.add(machine)
            session.commit()
        return machine

    def backup_start(self):
        """Add an entry to the database when a dirvish backup is started.

        This function should be triggered by dirvish pre-server.
        """
        dirvish_vault  = os.environ.get('DIRVISH_VAULT', None)
        dirvish_server = os.environ.get('DIRVISH_SERVER', None)
        dirvish_client = os.environ.get('DIRVISH_CLIENT', None)
        # dirvish_image  = os.environ.get('DIRVISH_IMAGE', None)

        machine = self.create_machine(
            dirvish_server,
            dirvish_vault,
            dirvish_client,
        )

        new_entry = DirvishEntry(
            datetime=datetime.now(),
            machine=machine.id,
            trigger='start',
        )

        db_session = sessionmaker(bind=self._engine)
        session = db_session()
        session.add(new_entry)
        session.commit()

    def backup_stop(self):
        """Add an entry to the database when a dirvish backup is stopped.

        This function should be triggered by dirvish post-server.
        """
        dirvish_vault  = os.environ.get('DIRVISH_VAULT', None)
        dirvish_server = os.environ.get('DIRVISH_SERVER', None)
        dirvish_client = os.environ.get('DIRVISH_CLIENT', None)
        # dirvish_image  = os.environ.get('DIRVISH_IMAGE', None)
        dirvish_status = os.environ.get('DIRVISH_STATUS', None)

        machine = self.create_machine(
            dirvish_server,
            dirvish_vault,
            dirvish_client,
        )

        new_entry = DirvishEntry(
            datetime=datetime.now(),
            machine=machine.id,
            trigger='end',
            status=dirvish_status,
        )

        db_session = sessionmaker(bind=self._engine)
        session = db_session()
        session.add(new_entry)
        session.commit()
