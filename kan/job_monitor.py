import os
import re
import time

def pkushow(jobid):
    shell = f"""
        ls --color=auto `pkujob {jobid} | grep Command | cut -d '=' -f 2` &&
        cat `pkujob {jobid} | grep Command | cut -d '=' -f 2`
    """
    return os.popen(shell).readlines()

def pkusq(jobid):
    grepres = os.popen(f'pkusq | grep {jobid}').readlines()
    runtime = re.sub('( )+',' ',grepres[0]).split(' ')[5]
    yield runtime

def pidinfo(pid):
    res = os.popen(f'ps aux | grep -v grep | grep " {pid} "').readlines()
    res = re.sub('( )+', ' ', res[0]).split(' ')
    starttime = ' '.join(res[8:10])
    command = ' '.join(res[10:])
    thedir = os.readlink(f'/proc/{pid}/cwd')
    yield starttime, command
