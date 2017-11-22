# -*- coding: utf-8 -*-
"""
Implement script entry point for glc.
"""

import invoke
import glc.config
import glc.defaults


class GlcConfig(invoke.Config):
    """
    Specialisation of Config for glc.
    """
    prefix = 'glc'

    @staticmethod
    def global_defaults():
        return invoke.config.merge_dicts(invoke.Config.global_defaults(),
                                         glc.defaults.settings())


class GlcProgram(invoke.Program):
    """
    Specialisation of Program for bun.
    """

    def core_args(self):
        core_args = super(GlcProgram, self).core_args()
        extra_args = []
        #    invoke.Argument(names=('pretend', 'dry-run'),
        #                    help="Show the commands which would be executed, but don't actually execute them"),
        #  ]
        return core_args + extra_args


# pylint: disable=invalid-name
program = GlcProgram(config_class=GlcConfig,
                     namespace=glc.config.collection(),
                     version='0.1.0')
