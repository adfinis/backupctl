=========
 bkpmgmt
=========

------------------------------------------------------------
 Manage dirvish backups with an underlying zfs storage pool
------------------------------------------------------------

:Author:
    Written by Tobias Rueetschi, Adfinis SyGroup AG.
:Date:
    April 2018
:Copyright:
    Copyright 2018 Adfinis SyGroup AG License GPLv3+:
    GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.
:Version:
    1.0
:Manual section:
    8
:Manual group:
    System Manager's Manual


SYNOPSIS
========

bkpmgmt COMMAND [OPTIONS]

bkpmgmt log

bkpmgmt [--help]


DESCRIPTION
===========
Tool to manage zfs volumes and create new dirvish vault configurations.


COMMANDS
========
All subcommands that modify zfs volumes and dirvish configurations.

new -n customer [-c server] [-s size]
-------------------------------------
Create a new customer zfs volume or a new dirvish vault inside a customer.

resize -n customer [-c server] -s size
--------------------------------------
Resize an existing customer zfs volume or dirvish vault inside a customer.
Shrinking is supported too.

remove -n customer [-c server]
------------------------------
Remove an existing customer zfs volume or dirvish vault inside a customer.
If removing a customer, all dirvish vaults inside this customer will be removed
too.

log
---
Show the history of generating, resizing and removing customers and servers.


OPTIONS
=======

-c, --client            Specify the hostname of the dirvish vault name.
--dirvish-client        Specify a client ip or fqdn to back up. Needed if
                        different from option client.
-h, --help              Show this help message and exit.
-n, --name              Customer name. Used as a logical group of dirvish
                        vaults.
-s, --size              Quota of a customer or a server. Size can be written
                        human readable as MB, GB and so on.


EXAMPLES
========

CUSTOMER MANAGEMENT
-------------------

Create a new customer with a quota of 10G.

  bkpmgmt new -n customer1 -s 10G

Resize the quota of an existing customer to 20G.

  bkpmgmt resize -n customer1 -s 20G

Remove a customer with all his servers. All data will be lost.

  bkpmgmt remove -n customer1

SERVER MANAGEMENT
-----------------

Create a new server www.example.com for customer1 with no special quota (it
will inherit the quota of the customer).

  bkpmgmt new -n customer1 -h www.example.com

Create a new server www.example.com for customer1 with a quota of 10G. Data
inside this server will also count on the customer level).

  bkpmgmt new -n customer1 -h www.example.com -s 10G

Create a new server www.example.com which isn't directly accessible, so a
special dirvish client is needed, in this case the server is reachable with the
ip address 192.0.2.100.

  bkpmgmt new -n customer1 -h www.example.com -s 10G --dirvish-client 192.0.2.100

Resize the quota of the server www.example.com of customer1 to the size of 20G.

  bkpmgmt resize -n customer1 -h www.example.com -s 20G

Remove the server www.example.com of customer1, this will delete all the backups
and also the dirvish configuration for this server.

  bkpmgmt remove -n customer1 -h www.example.com


SEE ALSO
========

``dirvish(8)``

.. vim: set et ts=2 sw=2 :
