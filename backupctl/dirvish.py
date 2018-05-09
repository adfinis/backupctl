#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

import jinja2

logger = logging.getLogger(__name__)

EXCLUDES_DEFAULT = [
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


def create_config(vault, client, excludes=EXCLUDES_DEFAULT):
    """Create default dirvish configuration.

    :param string vault:    Dirvish vault.
    :param string client:   Client fqdn or IP address.

    :returns: True if the dirvish configuration was written, else False.
    :rtype: bool
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config_path_j2 = os.path.join(root_dir, 'dirvish.conf.j2')
    config_root = os.path.join(
        '{0}'.format(vault),
        'dirvish',
    )
    config_path = os.path.join(
        config_root,
        'default.conf',
    )
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
    return True
