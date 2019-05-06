#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess

logger = logging.getLogger(__name__)


def new_filesystem(fs, path, size=None, compression=True):
    """Create a new zfs file system. The file system is automatically mounted
    according to the path property.

    :param string fs:           zfs file system.
    :param string path:         Mountpoint to mount the new file system.
    :param string size:         Size in a human readable format.
    :param bool compression:    Option to enable or disable the zfs internal
                                compression.

    :returns: True if the file system was created correctly, else False.
    :rtype: bool
    """
    if compression:
        compression = "compression=on"
    else:
        compression = "compression=off"
    if size is not None:
        size = ["-o", "quota={0}".format(size)]
    else:
        size = []

    returncode, stdout, stderr = execute_cmd(
        ["zfs", "create", "-o", compression, "-o", "dedup=off"]
        + size
        + ["-o", "mountpoint={0}".format(path), "{0}".format(fs)]
    )
    if returncode == 0:
        logger.info('created zfs file system "{0}" successfully'.format(fs))
        return True
    else:
        logger.error('create zfs file system "{0}" failed: {1}'.format(fs, stderr))
        return False


def resize_filesystem(fs, size):
    """Set a new zfs file system quota to a present zfs file system.

    :param string fs:           zfs file system.
    :param string size:         Size in a human readable format.

    :returns: True if the quota was set correctly, else False.
    :rtype: bool
    """
    if size.lower() != "none":
        usage = filesystem_usage(fs)
        if usage > parse_size(size):
            logger.warn(
                "new size ({0}) is smaller than used size ({1})".format(size, usage)
            )
            return False
    returncode, stdout, stderr = execute_cmd(
        ["zfs", "set", "quota={0}".format(size), "{0}".format(fs)]
    )
    if returncode == 0:
        logger.info(
            'set zfs file system quota for "{0}" to {1} successfully'.format(fs, size)
        )
        return True
    else:
        logger.error(
            'set zfs file system quota for "{0}" failed: {1}'.format(fs, stderr)
        )
        return False


def remove_filesystem(fs):
    """Remove an existing zfs file system. The file system is automatically
    unmounted.

    :param string fs:   zfs file system.

    :returns: True if the file system was removed correctly, else False.
    :rtype: bool
    """
    execute_cmd(["zfs", "set", "mountpoint=none", "{0}".format(fs)])
    returncode, stdout, stderr = execute_cmd(
        ["zfs", "destroy", "-r", "-f", "{0}".format(fs)]
    )
    if returncode == 0:
        logger.info('destroyed zfs file system "{0}" successfully'.format(fs))
        return True
    else:
        logger.error('destroy zfs file system "{0}" failed: {1}'.format(fs, stderr))
        return False


def filesystem_usage(fs):
    """Get the usage of a filesystem.

    :param string fs:   zfs file system.

    :returns: Number of used bytes or None if an error occured.
    :rtype: int
    """
    returncode, stdout, stderr = execute_cmd(
        ["zfs", "get", "-H", "-o", "value", "-p", "used", "{0}".format(fs)]
    )
    try:
        usage = int(stdout)
    except ValueError as e:
        logger.error('zfs returned not an integer as usage for "{0}"'.format(fs))
        return None
    if returncode == 0:
        logger.info('file system "{0}" use {1}B data'.format(fs, usage))
        return usage
    else:
        logger.error('destroy zfs file system "{0}" failed: {1}'.format(fs, stderr))
        return None


def parse_size(size):
    """Convert a human readable file system size ("B", "K", "M", "G", "T")
    into a number of bytes.

    :param string size: Human readable size.

    :returns: Number of bytes or None if an error occured.
    :rtype: int

    :raises ValueError: If size couldn't be interpreted.
    """
    SYMBOLS = {"customary": ("B", "K", "M", "G", "T", "P", "E", "Z", "Y")}
    init = size
    num = ""
    while size and size[0:1].isdigit() or size[0:1] == ".":
        num += size[0]
        size = size[1:]
    num = float(num)
    letter = size.strip()
    for name, sset in SYMBOLS.items():
        if letter in sset:
            break
    else:
        if letter == "k":
            # treat 'k' as an alias for 'K' as per: http://goo.gl/kTQMs
            sset = SYMBOLS["customary"]
            letter = letter.upper()
        else:
            raise ValueError("can't interpret %r" % init)
    prefix = {sset[0]: 1}
    for i, size in enumerate(sset[1:]):
        prefix[size] = 1 << (i + 1) * 10
    return int(num * prefix[letter])


def execute_cmd(command, stdin="", communicate=True):
    """Executes the given command (which should be a list).

    If you pass stdin, it will be written to the command's stdin.
    :param command:      the command to execute
    :type command:       list
    :param stdin:        will be written to the command's stdin
    :type stdin:         string
    :param communicate:  If False the helper will not communicate with the
                         process: useful for background process (otherwise
                         the command will block)
    :type communicate:   Boolean

    Returns a tuple of (returncode, stdout, stderr) upon completion.
    """

    returncode = 0
    is_shell = isinstance(command, str)
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_shell
    )
    if communicate:
        (stdout, stderr) = proc.communicate(stdin)
        returncode = proc.wait()
        return (returncode, stdout.decode("utf8"), stderr.decode("utf8"))
    return (None, None, None)
