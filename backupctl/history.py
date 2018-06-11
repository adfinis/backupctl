#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class HistoryEntry(Base):
    __tablename__ = 'history'

    id       = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    command  = Column(String)
    customer = Column(String)
    vault    = Column(String)
    size     = Column(String)

    def __repr__(self):
        return "<Entry(id='{0}')>".format(self.id)


class History:
    """Store and show history of commands done with the backupctl tool.

    :ivar sqlalchemy.engine.base.Engine engine: SQLAlchemy engine.

    :raises sqlalchemy.exc.ArgumentError: Raised when an invalid or conflicting
                                          function argument is supplied.
    :raises sqlalchemy.exc.OperationalError: Wraps a DB-API OperationalError.
    """

    def __init__(self, engine):
        self._engine = engine
        Base.metadata.create_all(engine)

    def add(self, customer, command, vault=None, size=None):
        """Add an entry to the history.

        :param string customer: Customer name.
        :param string command:  Used subcommand, e.g. create or resize.
        :param string vault:    Vault name or server hostname.
        :param string size:     Quota size.

        :returns: True
        :rtype: bool

        :raises sqlalchemy.exc.ArgumentError: Raised when an invalid or
                                              conflicting function argument is
                                              supplied.
        :raises sqlalchemy.exc.OperationalError: Wraps a DB-API
                                                 OperationalError.
        """
        new_entry = HistoryEntry(
            datetime=datetime.now(),
            command=str(command),
            customer=str(customer),
            vault=str(vault),
            size=str(size),
        )

        db_session = sessionmaker(bind=self._engine)
        session = db_session()

        session.add(new_entry)
        session.commit()
        return True

    def show(self, count=20):
        """Show the history.

        :param int customer:    Number of entries to show.

        :returns: A list of entries.
        :rtype: `list` of `string`

        :raises sqlalchemy.exc.ArgumentError: Raised when an invalid or
                                              conflicting function argument is
                                              supplied.
        :raises sqlalchemy.exc.OperationalError: Wraps a DB-API
                                                 OperationalError.
        """
        Base.metadata.bind = self._engine
        db_session = sessionmaker()
        db_session.bind = self._engine
        session = db_session()

        history_list = []
        entries = session.query(HistoryEntry).order_by(
            HistoryEntry.datetime
        )[-count:]

        for entry in entries:
            dt = str(entry.datetime)
            command = '{0}'.format(entry.command)
            customer = 'customer "{0}" '.format(entry.customer)
            if entry.vault != "None":
                vault = 'vault "{0}" '.format(entry.vault)
            else:
                vault = ''
            if entry.size != "None":
                size = 'with size {0} '.format(entry.size)
            else:
                size = ''

            history_list.append(
                '{0} - {1} {2}{3}{4}'.format(
                    dt,
                    command,
                    customer,
                    vault,
                    size,
                )
            )
        return history_list
