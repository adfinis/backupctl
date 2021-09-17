===========
 backupctl
===========

------------------------------------------------------------
 Manage dirvish backups with an underlying zfs storage pool
------------------------------------------------------------

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
    ${BACKUPCTL_VERSION}
:Manual section:
    8
:Manual group:
    System Manager's Manual


SYNOPSIS
=========

backupctl COMMAND [OPTIONS]

backupctl log

backupctl [--help]


DESCRIPTION
============
Tool to manage zfs volumes and create new dirvish vault configurations. This
tool depends on a already present zfs pool, normally called backup.
This tool (which is pronounced "backup cuddle") should be run with root
privileges, if not possible, at least zfs fuse access as user is needed
(to create new or remove existing zfs datasets and set quotas).
This is more tricky and may not be tested as well as zfs with the kernel
module.


COMMANDS
=========
All subcommands that modify zfs volumes and dirvish configurations.

new -n customer [-v server/vault] [-s size]
--------------------------------------------
Create a new customer zfs volume or a new dirvish vault inside a customer.

resize -n customer [-v server/vault] -s size
---------------------------------------------
Resize an existing customer zfs volume or dirvish vault inside a customer.
Shrinking is supported too, but if there is more data in the vault than the
size you're trying to shrink to an error will occur.
To unset a quota, set the parameter size to "none".

remove -n customer [-v server/vault]
-------------------------------------
Remove an existing customer zfs volume or dirvish vault inside a customer.
If removing a customer, all dirvish vaults inside this customer will be removed
too.

log
----
Show the history of generating, resizing and removing customers and servers.


OPTIONS
========

-v, --vault             Specify the hostname of the dirvish vault name.
--dirvish-client        Specify a client ip or fqdn to back up. Needed if
                        different from option client.
-h, --help              Show this help message and exit.
-n, --name              Customer name. Used as a logical group of dirvish
                        vaults.
-s, --size              Quota of a customer or a server. Size can be written
                        human readable as MB, GB and so on.


QUOTA
======
The storage used in a vault is substracted from the quota of the customer.
The quota of the customer should be equal or bigger than the one of the
vault/server, if this isn't the case, then the quota of the customer can't be
used in the full size. A quota must be defined for a customer. It may be
defined for a vault/server.
The summary of all quotas of vaults inside a customer can be bigger than the
quota of the customer.

Example
--------
As an example, if the ZFS pool is 50 GB, there is one customer with 40 GB, and
there are three vaults/servers with each 20 GB, each vault/server can use up to
20 GB, if all three vaults/servers are not more than 40 GB.

.. code-block::

  NAME                               USED  AVAIL  REFER
  backup                              35G    50G   205K
  backup/customer1                    35G    40G   273K
  backup/customer1/www1.example.com   10G    20G    10G
  backup/customer1/www2.example.com   10G    20G    10G
  backup/customer1/www3.example.com   15G    20G    15G


EXAMPLES
=========

CUSTOMER MANAGEMENT
--------------------

Create a new customer with a quota of 10G.

  backupctl new -n customer1 -s 10G

Resize the quota of an existing customer to 20G.

  backupctl resize -n customer1 -s 20G

Remove a customer with all his servers. All data will be lost.

  backupctl remove -n customer1

SERVER MANAGEMENT
------------------

Create a new server/vault www.example.com for customer1 with no special quota
(it will inherit the quota of the customer).

  backupctl new -n customer1 -v www.example.com

Create a new server/vault www.example.com for customer1 with a quota of 10G.
Data inside this server will also count on the customer level).

  backupctl new -n customer1 -v www.example.com -s 10G

Create a new server/vault www.example.com which isn't directly accessible, so a
special dirvish client is needed, in this case the server is reachable with the
ip address 192.0.2.100.

  backupctl new -n customer1 -v www.example.com -s 10G --dirvish-client 192.0.2.100

Resize the quota of the server/vault www.example.com of customer1 to the size
of 20G.

  backupctl resize -n customer1 -v www.example.com -s 20G

Remove the server/vault www.example.com of customer1, this will delete all the
backups and also the dirvish configuration for this server.

  backupctl remove -n customer1 -v www.example.com


EXIT STATUS
============
The following exit values are returned:

0
--
Successful completion.

1
--
An error occurred.

2
--
No command was given.


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

/var/lib/backupctl/backupctl.db
--------------------------------
backupctl history database. This is an sqlite3 database.


SEE ALSO
=========

* ``backupctl.ini(5)``, backupctl configuration file
* ``dirvish(8)``, dirvish backup utility

.. vim: set et ts=2 sw=2 :
