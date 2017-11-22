# -*- coding: utf-8 -*-
"""
Implements configuration discovery for glc
"""

from __future__ import print_function
import glob
import os
import yaml
import invoke
from invoke import task

import glc.build
import glc.defaults


def add_packages(glc_config, directory):
    """
    if directory exists then merge all configuration into the glc_config dict

    :param glc_config: existing dict config to merge new config into
    :param directory: directory which holds config to merge
    :return: merged dict of the original config plus config from directory
    """
    if os.path.isdir(directory):
        for config_file in glob.glob('{}/*.yaml'.format(directory)):
            invoke.config.merge_dicts(glc_config, yaml.load(open(config_file)))
    return glc_config


def settings():
    """
    generate a consolidated set of configuration for bun - if GLC_CONFIG_DIR is set
    then only read configuration from there; otherwise read config from the
    directory /etc/glc

    :return: a dict holding glc configuration
    """
    glc_config = invoke.config.copy_dict(glc.defaults.settings())

    if 'GLC_CONFIG_DIR' in os.environ:
        add_packages(bun_config, os.environ('GLC_CONFIG_DIR'))
    else:
        if os.path.isdir('/etc/glc'):
            add_packages(bun_config, '/etc/glc')

    return glc_config


def collection():
    """Return an invoke collection for glc"""
    # pylint: disable=invalid-name
    ns = invoke.Collection(
        glc.build.key,
        glc.build.status,
        glc.build.validate,
        glc.build.fetch,
        glc.build.zap_partial,
        glc.build.create,
        glc.build.copy,
        glc.config,
        glc.defaults)

    ns.configure(settings())

    return ns


@task(default=True)
def config(ctx):
    """
    dump configuration in effect to the console

    :param ctx: an invoke context object
    """
    print(yaml.dump(ctx.glc, default_flow_style=False))
