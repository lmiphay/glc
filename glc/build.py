# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import invoke
from invoke import task
import lxc
import requests
import sys

# extract with: tar xvjpf stage3-amd64-*.tar.bz2 --xattrs --numeric-owner
# see: https://wiki.gentoo.org/wiki/Sakaki%27s_EFI_Install_Guide/Installing_the_Gentoo_Stage_3_Files#Downloading.2C_Verifying_and_Unpacking_the_Gentoo_Stage_3_Tarball
# /usr/share/lxc/templates/lxc-gentoo:cache_stage3() is missing the --xattrs
#cache_setup(){
#    partialfs="${cacheroot}/partial-${arch}-${variant}"
    #if cache exists and flush not needed, return
#    [[ -d "${cachefs}" && -z "${flush_cache}" ]] && return 0
#cacheroot="${LXC_CACHE_PATH:-"/var/cache/lxc"}/gentoo"
#portage_cache="${cacheroot}/portage.tbz"
#cachefs="${cacheroot}/rootfs-${arch}-${variant}"

# Gentoo Linux Release Engineering (Automated weekly release key)
# See: https://wiki.gentoo.org/wiki/Project:RelEng#Keys
# Expires: 2019-08-22
REL_ENG_KEY_ID = '0xBB572E0E2D182910'
REL_ENG_KEY_FINGERPRINT='13EB BDBE DE7A 1277 5DFD  B1BA BB57 2E0E 2D18 2910'

@task(optional=['fetch'])
def key(ctx, fetch=None, key_id=REL_ENG_KEY_ID, fingerprint=REL_ENG_KEY_FINGERPRINT):
    """
    fetch/check the Rel Eng signing key
    """
    if fetch:
        ctx.run('gpg --keyserver hkp://pool.sks-keyservers.net:80 --recv-key {}'.format(key_id), echo=True)
    actual = ctx.run('gpg --fingerprint {}'.format(key_id), echo=True).stdout.split('\n')[1].strip()
    if actual != fingerprint:
        sys.exit('fingerprints do not match:\n  {} (expected)\n  {} (actual)\n'.format(fingerprint, actual))
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
        if ctx.run('gpg --verify {}.DIGESTS.asc'.format(tarball)):
            if ctx.run("""awk '/SHA512 HASH/{getline;print}' {}.DIGESTS.asc | sha512sum --check""".format(tarball)):
                print('{} validated'.format(tarball))
            else:
                sys.exit('checksum failed for: {}'.format(tarball))
        else:
                sys.exit('signature verification failed for: {}.DIGESTS.asc'.format(tarball))
        #ctx.run('openssl dgst -r -sha512 {}'.format(tarball))
        #ctx.run('openssl dgst -r -whirlpool {}'.format(tarball))


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
