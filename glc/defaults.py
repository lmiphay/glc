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
        'key': {
            # Gentoo Linux Release Engineering (Automated weekly release key)
            # See: https://wiki.gentoo.org/wiki/Project:RelEng#Keys
            # Expires: 2019-08-22
            'key_id': '0xBB572E0E2D182910',
            'fingerprint': '13EB BDBE DE7A 1277 5DFD  B1BA BB57 2E0E 2D18 2910'  # note extra space in the middle
        },
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
