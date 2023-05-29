#!/usr/bin/python3

import time
import subprocess

backup_folder = "data"
data_folder = "tmp"

t = time.gmtime()
pos = time.strftime('%e%m%Y%H%M%S', t)

filename = '%s/data-%s.tgz' % (backup_folder, pos)
cmd = "tar cfz %s %s" % (filename, data_folder)

subprocess.call([cmd], shell=True)
