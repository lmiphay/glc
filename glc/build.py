# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import invoke
from invoke import task
import lxc
import requests
import StringIO
import sys


def has_key(ctx, fingerprint):
    compact = fingerprint.replace(' ', '')
    return 'fpr:::::::::{}:'.format(compact) in ctx.run('gpg --list-public-keys --with-colons').stdout


@task(optional=['fetch'])
def key(ctx, fetch=None):
    """
    fetch/check the Rel Eng signing key
    """
    if fetch or not has_key(ctx.glc.key.fingerprint):
        ctx.run('gpg --keyserver hkp://pool.sks-keyservers.net:80 --recv-key {}'.format(ctx.glc.key.key_id), echo=True)
    actual = ctx.run('gpg --fingerprint {}'.format(ctx.glc.key.key_id), echo=True).stdout.split('\n')[1].strip()
    if actual != ctx.glc.key.fingerprint:
        sys.exit('fingerprints do not match:\n  {} (expected)\n  {} (actual)\n'.format(ctx.glc.key.fingerprint, actual))
    else:
        print('key fingerprints match')


def latest_stage3(glc):
    """
    # Latest as of Tue, 21 Nov 2017 12:30:01 +0000
    # ts=1511267401
    20171116/stage3-amd64-20171116.tar.bz2 247819283
    """
    url = '{}/{}'.format(glc.stage_server.url_base, glc.stage_server.latest_stage3).format(**glc)
    return requests.get(url).content.decode('utf8').split('\n')[2].split()[0]


@task
def status(ctx):
    print('latest stage3 (remote): {}'.format(latest_stage3(ctx.glc)))
    if os.path.isdir(ctx.glc.cache_dir):
        with ctx.cd(ctx.glc.cache_dir):
            print('latest stage3 (local): {}'.format(ctx.run("""ls -t | sed 's/^/   /'""").stdout.strip()))
    else:
        print('latest stage3 (local): directory does not exist ({})'.format(ctx.glc.cache_dir))


@task
def validate(ctx, tarball):
    with ctx.cd(ctx.glc.cache_dir):
        if not ctx.run('gpg --verify {}.DIGESTS.asc'.format(tarball)):
            sys.exit('signature verification failed for: {}.DIGESTS.asc'.format(tarball))
        with open('{}.DIGESTS.asc'.format(tarball), 'r') as digests:
            line = digests.readline()
            while line:
                if 'SHA512 HASH' in line:
                    checksum, hash_content = 'sha512sum', digests.readline()
                elif 'WHIRLPOOL HASH' in line:
                    checksum, hash_content = 'whirlpool-hash', digests.readline()
                else:
                    continue
                if not ctx.run('{} --check'.format(checksum), in_stream=StringIO(hash_content)):
                    sys.exit('{} checksum failed for: {}'.format(line, hash_content))
                line = digests.readline()


@task  # (post=[validate])
def fetch(ctx):
    if not os.path.isdir(ctx.glc.cache_dir):
        sys.exit('please make {} first'.format(ctx.glc.cache_dir))  # os.makedirs(ctx.glc.cache_dir)
    with ctx.cd(ctx.glc.cache_dir):
        stage3 = latest_stage3(ctx.glc)
        url = '{url_base}/{stage3}'.format(url_base=ctx.glc.stage_server.url_base, stage3=stage3).format(**ctx.glc)
        for suffix in ['', '.CONTENTS', '.DIGESTS', '.DIGESTS.asc']:
            ctx.run('wget {url}{suffix}'.format(url=url, suffix=suffix), echo=True)
        validate(ctx, os.path.basename(stage3))
        ctx.run('ln -sf {new_stage3} {latest_tarball}'.format(new_stage3=os.path.basename(stage3), **ctx.glc), echo=True)

@task
def zap_partial(ctx):
    with ctx.cd(ctx.glc.template.cacheroot):
        ctx.run('rm -rf partial-{arch}-{variant}'.format(**ctx.glc))

        
@task(pre=[zap_partial], post=[zap_partial])
def create(ctx, base_name):
    base = lxc.Container(base_name)
    ctx.glc.template.opts.tarball = ctx.glc.template.opts.tarball.format(**ctx.glc)
    base.create(template=ctx.glc.template.name,
                flags=0, # lxc.LXC_CREATE_QUIET,
                args=ctx.glc.template.opts)


@task
def copy(ctx, base_name, new_container_name):
    base = lxc.Container(base_name)
    new_container = base.clone(newname=new_container_name,
                               flags=lxc.LXC_CLONE_SNAPSHOT,
                               bdevtype=ctx.glc.backingstorage)
