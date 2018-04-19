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
