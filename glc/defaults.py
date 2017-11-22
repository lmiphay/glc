# -*- coding: utf-8 -*-
"""
Implementation of builtin defaults for glc
"""

from __future__ import print_function
import os
import yaml

from invoke import task

DEFAULT_CONFIG = {
    'glc': {
        'arch': 'amd64',
        'variant': 'amd64',
        'backingstorage': 'overlay',
        'cache_dir': '/var/cache/glc',
        'latest_tarball': 'STAGE3-LATEST.tar.bz2',
        'stage_server': {
            'url_base': 'http://distfiles.gentoo.org/releases/{arch}/autobuilds',
            'latest_stage3': 'latest-stage3-{arch}.txt',
        },
        'template': {
            'name': 'gentoo',
            'cacheroot': '{}/gentoo'.format(os.getenv('LXC_CACHE_PATH', '/var/cache/lxc')),
            'opts': {
                'tarball': '{cache_dir}/{latest_tarball}'
            }
        }
    }
}


def settings():
    """Returns the unaltered default built-in configuration for glc"""
    return DEFAULT_CONFIG


@task(default=True)
def defaults(ctx):  # pylint: disable=unused-argument
    """
    dump the default settings to the console
    :param ctx: an invoke context object
    """
    print(yaml.dump(settings(), default_flow_style=False))
