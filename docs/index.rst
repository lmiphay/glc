.. glc documentation master file, created by
   sphinx-quickstart on Wed Sep 20 19:58:52 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========================
Welcome to glc!
========================

Linux Container Creation for Gentoo
--------------------------------------

``glc`` is a simple lxc creator program built on top of lxc(1) and
`invoke <http://www.pyinvoke.org/>`_ tasks.

The philosophy is to:

+ delegate as much as possible to lxc(1)
+ very configurable in `yaml <http://www.yaml.org/>`_
+ wraps individual operations with `invoke <http://www.pyinvoke.org/>`_ tasks
+ integrates with `oam <https://github.com/lmiphay/oam>`_
+ installable via emerge/layman

See :doc:`changelog` for changes in this version.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
