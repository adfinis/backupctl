#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from subprocess import PIPE, Popen

logger = logging.getLogger(__name__)


def new_filesystem(fs, path, size, compression=True):
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
        compression = 'compression=on'
    else:
        compression = 'compression=off'
    proc = Popen(
        [
            'sudo',
            'zfs',
            'create',
            '-o',
            compression,
            '-o',
            'dedup=off',
            '-o',
            'quota={0}'.format(size),
            '-o',
            'mountpoint={0}'.format(path),
            '{0}'.format(fs),
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode is 0:
        logger.info('created zfs file system "{0}" successfully'.format(
            fs,
        ))
        return True
    else:
        logger.error('create zfs file system "{0}" failed: {1}'.format(
            fs,
            stderr,
        ))
        return False


def resize_filesystem(fs, size):
    """Set a new zfs file system quota to a present zfs file system.

    :param string fs:           zfs file system.
    :param string size:         Size in a human readable format.

    :returns: True if the quota was set correctly, else False.
    :rtype: bool
    """
    usage = filesystem_usage(fs)
    if usage > parse_size(size):
        logger.warn("new size ({0}) is smaller than used size ({1})".format(
            size,
            usage,
        ))
        return False
    proc = Popen(
        [
            'sudo',
            'zfs',
            'set',
            'quota={0}'.format(size),
            '{0}'.format(fs),
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode is 0:
        logger.info(
            'set zfs file system quota for "{0}" to {1} successfully'.format(
                fs,
                size,
            )
        )
        return True
    else:
        logger.error('set zfs file system quota for "{0}" failed: {1}'.format(
            fs,
            stderr,
        ))
        return False


def remove_filesystem(fs):
    """Remove an existing zfs file system. The file system is automatically
    unmounted.

    :param string fs:   zfs file system.

    :returns: True if the file system was removed correctly, else False.
    :rtype: bool
    """
    proc = Popen(
        [
            'sudo',
            'zfs',
            'set',
            'mountpoint=none',
            '{0}'.format(fs),
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = proc.communicate()
    proc = Popen(
        [
            'sudo',
            'zfs',
            'destroy',
            '-f',
            '{0}'.format(fs),
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode is 0:
        logger.info('destroyed zfs file system "{0}" successfully'.format(
            fs,
        ))
        return True
    else:
        logger.error('destroy zfs file system "{0}" failed: {1}'.format(
            fs,
            stderr,
        ))
        return False


def filesystem_usage(fs):
    """Get the usage of a filesystem.

    :param string fs:   zfs file system.

    :returns: Number of used bytes or None if an error occured.
    :rtype: int
    """
    proc = Popen(
        [
            'sudo',
            'zfs',
            'get',
            '-H',
            '-o',
            'value',
            '-p',
            'used',
            '{0}'.format(fs),
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = proc.communicate()
    try:
        usage = int(stdout)
    except ValueError as e:
        logger.error('zfs returned not an integer as usage for "{0}"'.format(
            fs,
        ))
        return None
    if proc.returncode is 0:
        logger.info('file system "{0}" use {1}B data'.format(
            fs,
            usage,
        ))
        return usage
    else:
        logger.error('destroy zfs file system "{0}" failed: {1}'.format(
            fs,
            stderr,
        ))
        return None


def parse_size(size):
    """Convert a human readable file system size ("B", "K", "M", "G", "T")
    into a number of bytes.

    :param string size: Human readable size.

    :returns: Number of bytes or None if an error occured.
    :rtype: int

    :raises ValueError: If size couldn't be interpreted.
    """
    SYMBOLS = {
        'customary': ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
    }
    init = size
    num = ""
    while size and size[0:1].isdigit() or size[0:1] == '.':
        num += size[0]
        size = size[1:]
    num = float(num)
    letter = size.strip()
    for name, sset in SYMBOLS.items():
        if letter in sset:
            break
    else:
        if letter == 'k':
            # treat 'k' as an alias for 'K' as per: http://goo.gl/kTQMs
            sset = SYMBOLS['customary']
            letter = letter.upper()
        else:
            raise ValueError("can't interpret %r" % init)
    prefix = {sset[0]: 1}
    for i, size in enumerate(sset[1:]):
        prefix[size] = 1 << (i + 1) * 10
    return int(num * prefix[letter])
