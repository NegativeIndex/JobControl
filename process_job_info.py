#!/usr/bin/env python
"""
Read job.info files, analyze them and display the results nicely. 
"""
import sys,os
import subprocess
import glob
import re
import datetime,time
from termcolor import colored, cprint
import numpy as np
import logging
sys.path.append("/Users/wdai11/python-study")
from  JobControl.Optparse_Addon import *
from  JobControl.Job_Info import *
   

#########################
# main function
def main(argv):
    """Process the options, then find all the job,info file, analyze
    them, generate a report

    """   
    # logger
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(message)s')

    # option process
    str1='Usage: %prog <dir> '
    str2='-maxdepth <int> '
    str4='This function read out job.info files.'
    str5='It passes the unknown options to find function.'
    parser = PassThroughOptionParser(usage=str1+str2,
                                     description=str4+str5)
 
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
    # logging.debug("Saved args are {}".format(sargs))
    # logging.debug("Accepted options is {}".format(opts))
    # logging.debug("Unkonwn args are {}".format(unk_args))


    # find all the folders which contains simulations
    comm=["find"]+unk_args+['-name','job.info']
    res = subprocess.check_output(comm).decode("ascii").rstrip()
    jobfiles=res.split('\n')
    jobfiles=[os.path.abspath(f) for f in jobfiles
              if len(f.strip())]
    jobfiles.sort()
    # for f in jobfiles:
    #     logging.debug(f)
              
    # build Simulation objects  
    sims=[Simulation.from_jobinfo(f) for f in jobfiles]
    # for s in sims:
    #     logging.debug(s)

    # organize data and generate output
    if not opts.summary:
        print('='*50)
        for s in sims:
            print(s.folder)
            print(s.short_str())
            if s.status=='abnormal':
                print(s.message)

            
 
    # build statistics
    nt=len(sims)
    nf=sum(1 for s in sims if s.status=='finished')

    # print unfinished
    if opts.unfinished and nt>nf:
        print('='*50)
        for s in sims:
            if s.status!='Finished':
                print(s.folder)
                print(s.short_str())
                if s.status=='abnormal':
                    print(s.message)
             
    # print longest finished simulations
    if opts.count>0:
        finished_sims=[s for s in sims if s.status=='finished']
        count=min((opts.count,nf))
        # logging.debug(count)
        print('='*50)
        sort_sims=sorted(finished_sims,key=lambda s:s.time,reverse=True)
        for idx in range(count):
            s=sort_sims[idx]
            print(s.folder)
            print("No.{}, time used: {:0.2f} hours".format(idx,s.time/3600))
       

    # print summary
    print('='*50)
    text=colored('{}/{}'.format(nf,nt), 'red')
    print(text+" jobs were finished based on job.info files")

         
 



#########################
# main function
if __name__=='__main__':
    main(sys.argv)
