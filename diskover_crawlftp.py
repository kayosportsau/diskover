#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""diskover - Elasticsearch file system crawler
diskover is a file system crawler that index's
your file metadata into Elasticsearch.
See README.md or https://github.com/shirosaidev/diskover
for more information.

Copyright (C) Chris Park 2017-2019
diskover is released under the Apache 2.0 license. See
LICENSE for the full license text.
"""

from diskover import config
from datetime import datetime
import sys
import dateutil.parser as dp
import ftplib
import os


def ftp_connection():
    """Connect to ftp server and return ftp connection object
    or False if unable to connect.
    """
    ftp_server = config['ftp_server']
    if ftp_server == "":
        return None
    ftp_user = config['ftp_user']
    ftp_password = config['ftp_password']
    if config['ftp_usetls'] == "true":
        tls = True
    else:
        tls = False
    if config['ftp_usepasv'] == "true":
        pasv = True
    else:
        pasv = False
    # connect to ftp server and login
    try:
        if tls:
            ftp = ftplib.FTP_TLS(ftp_server)
        else:
            ftp = ftplib.FTP(ftp_server)
        ftp.login(ftp_user, ftp_password)
        # ftp.set_debuglevel(10)
        if tls:
            ftp.prot_p()
        # ftp.set_pasv(pasv)
    except ftplib.all_errors as ftp_err:
        print("Error connecting to ftp server, exiting (%s)" % ftp_err)
        sys.exit(1)
    except Exception as err:
        print("Error connecting to ftp server, exiting (%s)" % err)
        sys.exit(1)
    else:
        return ftp

def ftp_cwd(path, ftp):
    print(f">>> CWD: {path}")
    curr = ftp.pwd()
    print("--- CURRENT: ", curr)
    ftp.cwd(os.path.basename(path))
    print("--- CURRENT: ", ftp.pwd())

def ftp_stat(path, ftp):
    print(f"FTP STAT: path:::: {path}" )
    _path = path
    if not path.endswith('/'):
        path = path + '/'
    if not path.startswith('/'):
        path = '/' + path

    
    curr = ftp.pwd()
    print("--- CURRENT: ", curr)

    # ftp.cwd(path)
    # curr2 = ftp.pwd()
    print( f"---- old pwd: curr {curr}" )

    lines = []
    ftp.retrlines('LIST', lines.append)
    print( f"----- lines: {len(lines)}" )
    # ftp.cwd(os.path.basename(_path))

    for line in lines:
        print( f"----line: {line}, {os.path.basename(_path)}" )
        itemlist = line.split(' ')
        itemlist = [x for x in itemlist if x]
        print(">>>>>> ", itemlist)
        print(f"itemlist[-1] >>>>>> [{itemlist[-1]}]")
        print(f"os.path.basename(_path) :[{os.path.basename(_path)}]")

        uid = itemlist[2]
        gid = itemlist[3]
        ctime = dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp()
        atime = dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp()
        mtime = dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp()
        nlink = itemlist[1]
        ino = 0
        size = itemlist[4]
        mode = 0
        dev = 0

        if itemlist[-1] == os.path.basename(_path): 
            print("********FOUND A MATCH!!!!!")
            break

    return mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime	
	


# def ftp_stat(path, ftp):
#     _path = path
#     if not path.endswith('/'):
#         path = path + '/'
#     if not path.startswith('/'):
#         path = '/' + path
#     ftp.cwd(path)
#     lines = []
#     lines = ftp.retrlines('LIST', lines.append)
#     for line in lines:
#         itemlist = line.split(' ')
#         itemlist = [x for x in itemlist if x]
#         if itemlist[-1] is os.path.basename(_path):
#             uid = itemlist[2]
#             gid = itemlist[3]
#             ctime = dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp()
#             atime = dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp()
#             mtime = dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp()
#             nlink = itemlist[1]
#             ino = 0
#             size = itemlist[4]
#             mode = 0
#             dev = 0
#             break

#     return mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime


def ftp_listdir(path, ftp):
    print(f"\n\n*******************Got Request to list: {path}")
    dirs = []
    nondirs = []

    # get path metadata
    path_metadata = ftp_stat(path, ftp)
    root = (path, path_metadata)

    # get directory list
    lines = []
    ftp.retrlines('LIST', lines.append)
    for line in lines:
        itemlist = line.split(' ')
        itemlist = [x for x in itemlist if x]

        for itm in itemlist:
            print("----: ", itm)

        if itemlist[0].startswith('d') and itemlist[0] not in ('.', '..'):
            dirs.append(
                (
                    os.path.join(path, itemlist[-1]),
                    (
                        0,  # mode
                        0,  # inode 
                        0,  # dev
                        itemlist[1],  # numlinks
                        itemlist[2],  # uid
                        itemlist[3],  # gid
                        itemlist[4],  # size
                        dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp(),
                        dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp(),
                        dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp()
                    )
                )
            )
        elif itemlist[0].startswith('-'):
            nondirs.append(
                (
                    os.path.join(path, itemlist[-1]),
                    (
                        0,  # mode
                        0, 
                        0,  # dev
                        itemlist[1],  # numlinks
                        itemlist[2],  # uid
                        itemlist[3],  # gid
                        itemlist[4],  # size
                        dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp(),
                        dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp(),
                        dp.parse(itemlist[5] + ' ' + itemlist[6] + ' ' + itemlist[7]).timestamp(),
                        0  # blocks
                    )
                )
            )

    return root, dirs, nondirs


def ftp_add_diskspace(es, index, path, ses, logger):
    # there is no real way to get diskspace stats over ftp (that i'm aware of), so put dummy values
    indextime_utc = datetime.utcnow().isoformat()
    data = {
        "path": path,
        "total": 999999999,
        "used": 999999999,
        "free": 999999999,
        "available": 999999999,
        "indexing_date": indextime_utc
    }
    logger.info('Adding disk space info to es index')
    es.index(index=index, doc_type='diskspace', body=data)