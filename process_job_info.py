#!/usr/bin/env python
"""
Read job.info files, analyze them and display the results nicely. 
"""

import sys
import subprocess
import datetime,time
import re
import os,glob,time
import random,math
from termcolor import colored, cprint
import numpy as np
import logging
from optparse import (OptionParser,BadOptionError,AmbiguousOptionError)

###########################
## Collect the information from job.info, 
## then calculate the simulation time



   

#####################
# read job.info and get simulation time in seconds
def process_a_file(jobfile):
    job0=[] # begin job
    time0=[]
    job1=[] # end job
    time1=[]
    with open(jobfile, 'r') as f:
        mfile=f.readlines()

    for line in mfile:
        line=line.rstrip()
        # logging.debug(line) 
        if re.search('^\+',line):
            cjob=job0
            ctime=time0
        if re.search('^-----------',line):
            cjob=job1
            ctime=time1
        try:
            tt=time.strptime(line,"%a %b %d %H:%M:%S %Z %Y")
            ctime.append(time.mktime(tt))
        except ValueError:
            pass
        mobj=re.search('^[0-9]+',line)
        if mobj:
            cjob.append(mobj.group())
    
    # logging.debug(job0)
    # logging.debug(time0)
    # logging.debug(job1)
    # logging.debug(time1)
    
    # job finish is defined when I find an begin.end pair
    stime=None
    status=''
    info=''
    for jobid,t1 in zip(reversed(job1),reversed(time1)):
        # logging.debug("{} at {}".format(jobid,t1))
        try: 
            idx=job0.index(jobid)
            t0=time0[idx]
            stime=t1-t0
            status='d' # finished
            info=''
        except ValueError:
            pass
        if stime is not None:
            break
    # logging.debug(stime)
    # job is not finished
    if stime is None:
        folder=os.path.dirname(jobfile)
        os.chdir(folder)
        fbs=glob.glob("fb*txt")
        rfbs=[] 
        # get job status
        status='s' # job is stopped
        now=time.time()
        for fb in fbs:
            mod_time=os.path.getmtime(fb)
            if abs(mod_time-now)<600:
                status='r'
                rfbs.append(fb)
        # get running time
        if status=='r':
            for fb in rfbs:
                mobj=re.search('([0-9]+)\.txt',fb)
                fbid=mobj.group(1)
            
        logging.debug(fbid)
        logging.debug(fbs)
        logging.debug(rfbs)


    return (status,stime,info)



    
  


#########################
# main function
def main(argv):
    # logger
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(message)s')

    str1='Usage: %prog <dir> '
    str2='-maxdepth <int> '
    str4='This function read out job.info files.'
    str5='It passes the unknown options to find function.'
    parser = PassThroughOptionParser(usage=str1+str2,
                                     description=str4+str5)
    # parser = OptionParser()
    # convert args help 
    # if args.help:
    #     help_string = parser.format_help()
    #     print(help_string.replace('--', '-'))
    #     parser.exit(0)

    # for fun
    parser.add_option("-u", "--unfinished",
                      action="store_true",
                      default=False,
                      help="Demonstrate unfinished folders.")

    parser.add_option("-s", "--summary",
                      action="store_true",
                      default=False,
                      help="Demonstrate only summary.")

    parser.add_option("-c", "--count",type=int, default=0,
                      help="Demonstrate the longest jobs.")


    sargs=long_option_dash_1to2(argv)
    (opts,unk_args) = parser.parse_args(sargs)
    unk_args=long_option_dash_2to1(unk_args)

    # process unk_args
    unk_args.pop(0)  # remove the first
    # folders=[]
    # while unk_args:
    #     arg=unk_args[0]
    #     if re.search('^-',arg):
    #         break
    #     else:
    #         folders.append(unk_args.pop(0))

    # logging.debug(unk_args)
    # logging.debug(folders)
    logging.debug("Saved args are {}".format(sargs))
    logging.debug("Accepted options is {}".format(opts))
    logging.debug("Unkonwn args are {}".format(unk_args))


    # find all the folders which contains simulations
    comm=["find"]+['-name','job.info']
    res = subprocess.check_output(comm).decode("ascii").rstrip()
    jobfiles=res.split('\n')
    jobfiles=[os.path.abspath(jobfile) for jobfile in jobfiles]

    jobfiles.sort()
    tlist=[None]*len(jobfiles)
    slist=[None]*len(jobfiles)

    nt=len(jobfiles)
    nf=0
    for idx,jobfile in enumerate(jobfiles):
        # logging.debug(jobfile)
        folder=os.path.dirname(jobfile)
        status,stime,info=process_a_file(jobfile)
        if status=='d':
            nf+=1
            tlist[idx]=stime/3600
            slist[idx]=status
            if not opts.summary:
                print(folder)
                print("Time used: {:0.2f} hours".format(stime/3600))
        else:
            if not opts.summary:
                print(folder)
                print("Time used: None")

        # build summary
        print('='*30)
        text=colored('{}/{}'.format(nf,nt), 'red')
        print(text+" jobs were finished based on job.info files")

        if opts.unfinished and nt>nf:
            print('-'*30)
            print('Unfinished folders are')
            for idx,status in enumerate(slist):
                if status!='d':
                    folder=os.path.dirname(jobfiles[idx])
                    print(folder)
            
         
        if opts.count>0:
            count=min((opts.count,nf))
            logging.debug(count)
            idxes=np.argsort(tlist)
            print('-'*40)
            print('Longest simulations are: ')
            for ii in range(count):
                idx=idxes[-1-ii]
                folder=os.path.dirname(jobfiles[idx])
                print(folder)
                print("Time used: {:0.2f} hours".format(tlist[idx]))
        print('='*30)



#########################
# main function
if __name__=='__main__':
    main(sys.argv)
