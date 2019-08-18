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
import os
import ftplib
from optparse import OptionParser
import dateutil.parser as dp


def ftp_stat(path, ftp):
    print(f"FTP STAT: path:::: {path}" )
    _path = path
    if not path.endswith('/'):
        path = path + '/'
    if not path.startswith('/'):
        path = '/' + path

    
    curr = ftp.pwd()
    print("--- CURRENT: ", curr)

    # 
    # curr2 = ftp.pwd()
    print( f"---- old pwd: curr {curr}" )

    lines = []
    ftp.retrlines('LIST', lines.append)
    print( f"----- lines: {len(lines)}" )

    ftp.cwd(os.path.basename(_path))

    for line in lines:
        print( f"----line: {line}, {os.path.basename(_path)}" )
        itemlist = line.split(' ')
        itemlist = [x for x in itemlist if x]
        print(">>>>>> ", itemlist)
        print(f"itemlist[-1] >>>>>> [{itemlist[-1]}]")
        print(f"os.path.basename(_path) :[{os.path.basename(_path)}]")

        if itemlist[-1] == os.path.basename(_path):
            print("********FOUND A MATCH!!!!!")
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
            break

    return mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime	







version = '0.1-b1'
__version__ = version

parser = OptionParser(version="diskover ftp client v % s" % version)
parser.add_option("-s", "--server", metavar="HOST",
                    help="FTP server hostname/ip")
parser.add_option("-u", "--user", metavar="USERNAME",
                    help="Username")
parser.add_option("-p", "--password", metavar="PASSWORD",
                    help="Password")              
(options, args) = parser.parse_args()
options = vars(options)

HOST = options['server']
USER =  options['user']
PASSWORD = options['password']

ftp = ftplib.FTP(HOST)
ftp.set_debuglevel(9)
ftp.login(USER, PASSWORD)

data = []

ftp.dir(data.append)

print("---- : ", len(data))

for line in data:
    print("-", line)

ftpStat = ftp_stat("/MXF/default", ftp)

print("-----: ", ftpStat)

ftp.quit()



