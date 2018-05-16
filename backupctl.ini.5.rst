===============
 backupctl.ini
===============

------------------------------------------
 Configuration file for **backupctl(8)**.
------------------------------------------

:Author:
    Written by Tobias Rueetschi, Adfinis SyGroup AG.
:Date:
    May 2018
:Copyright:
    Copyright 2018 Adfinis SyGroup AG License GPLv3+:
    GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.
:Version:
    1.0
:Manual section:
    5
:Manual group:
    File Formats


DESCRIPTION
============
backupctl uses a configuration file at one of the three locations
(priority decreasing):

* $PWD/backupctl.ini
* $XDG_CONFIG_HOME/backupctl.ini
* /etc/backupctl.ini

If an option is found in a higher priority configuration file, it will overwrite
the option of any lower priority configuration file.


PARAMETERS
===========
There are two types of sections in the backupctl configuration file(s): database
and ZFS. ZFS defines the options regarding the ZFS setup and file system
configuration of the system. Database is used for the database configuration of
backupctl.


[database] OPTIONS
===================
In the [database] section it's possible to configure backupctl which database it
should use. At the moment there is just one option:

path
  File path for the sqlite3 database. The file will be created if it doesn't
  exists. The default is \`/var/lib/backupctl.db'.


[zfs] OPTIONS
==============

The [zfs] section is the place where it's possible to configure how the zfs is
setup on the system and where the dirvish bank is.
It consists of the following options:

pool
  The ZFS pool name which should be used for to create the file systems in it.
  This pool must already exist and you can find the name of it with
  \`zpool list'.

root
  The dirvish bank where the zfs file systems should be mounted to. This is an
  absolute path on you system, most certainly \`/srv/backups' or something like
  that.


EXAMPLES
=========
An basic example of the configuration file is:

.. code-block::

  [database]
  path = /var/lib/backupctl.db

  [zfs]
  pool = backup
  root = /srv/backup


FILES
======

/etc/backupctl.ini
-------------------
System-wide configuration file.

$XDG_CONFIG_HOME/backupctl.ini
-------------------------------
User specific configuration file. Will overwrite the configuration options of
the system-wide configuration file.

$PWD/backupctl.ini
-------------------
Local configuration file. Will overwrite the configuration options of any
previous configuration file.


SEE ALSO
=========

``backupctl(8)``
