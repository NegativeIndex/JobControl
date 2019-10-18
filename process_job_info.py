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
    for f in jobfiles:
        logging.debug(f)
              
        

    # tlist=[None]*len(jobfiles)
    # slist=[None]*len(jobfiles)

    # nt=len(jobfiles)
    # nf=0
    # for idx,jobfile in enumerate(jobfiles):
    #     # logging.debug(jobfile)
    #     folder=os.path.dirname(jobfile)
    #     status,stime,info=process_a_file(jobfile)
    #     if status=='d':
    #         nf+=1
    #         tlist[idx]=stime/3600
    #         slist[idx]=status
    #         if not opts.summary:
    #             print(folder)
    #             print("Time used: {:0.2f} hours".format(stime/3600))
    #     else:
    #         if not opts.summary:
    #             print(folder)
    #             print("Time used: None")

        # # build summary
        # print('='*30)
        # text=colored('{}/{}'.format(nf,nt), 'red')
        # print(text+" jobs were finished based on job.info files")

        # if opts.unfinished and nt>nf:
        #     print('-'*30)
        #     print('Unfinished folders are')
        #     for idx,status in enumerate(slist):
        #         if status!='d':
        #             folder=os.path.dirname(jobfiles[idx])
        #             print(folder)
            
         
        # if opts.count>0:
        #     count=min((opts.count,nf))
        #     logging.debug(count)
        #     idxes=np.argsort(tlist)
        #     print('-'*40)
        #     print('Longest simulations are: ')
        #     for ii in range(count):
        #         idx=idxes[-1-ii]
        #         folder=os.path.dirname(jobfiles[idx])
        #         print(folder)
        #         print("Time used: {:0.2f} hours".format(tlist[idx]))
        # print('='*30)



#########################
# main function
if __name__=='__main__':
    main(sys.argv)
