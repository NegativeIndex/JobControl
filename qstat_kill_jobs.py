#!/usr/bin/env python

import sys
import subprocess
import datetime 
import re
import os,glob,time
import argparse
from termcolor import colored, cprint

sys.path.insert(0,'/Users/wdai11/bin/Python_Library')
import my_python as mypy


#########################
##  kill all jobs
def kill_all_jobs(qjobs,forever=False,submit=False):
    text=colored('Danger: kill all the jobs!!', 'red')
    userInput = input(text+' y/n?  ');
    if userInput!='y':
        sys.exit('')

    count=0
    if forever or submit:
        for job in qjobs: job.get_folder()
    for job in qjobs:
        if forever or submit:
            job.get_folder()
            print(job)
            mypy.kill_job(job,restart=False)
            if submit:
                mypy.submit_job(path=job.folder)
        else:
            print(job)
            mypy.kill_job(job,restart=True)

        count+=1
        print('-'*25)
    print('No. of jobs precessed: {}'.format(count))

#############################
## find jobs and kill it
def kill_some_jobs(qjobs,path,status,forever=False,submit=False):
    count=0
    rfolder=os.path.abspath(path)
    for job in qjobs:
        if (status is None) or (job.status==status):
            job.get_folder()
            if job.folder and (rfolder in job.folder):
                os.chdir(job.folder)
                print(job)
                mypy.kill_job(job,restart=(not forever))
                if submit:
                    mypy.submit_job(path=job.folder)
                os.chdir(rfolder)
                count+=1
                print('-'*25)
    print('No. of jobs processed: {}'.format(count))    

## kill one job based on id
def kill_one_job(fid,forever=False,submit=False):
    pass
       
##################################
## main function
if __name__== "__main__":

    # parse args
    parser = argparse.ArgumentParser(description='kill cluster jobs')
    parser.add_argument('-a', '--all', action='store_true', 
                        help="Danger: kill all the jobs")

    parser.add_argument('-p', '--path', 
                        default='./',
                        help="Kill all the jobs in the path")

    parser.add_argument('-s', '--status', 
                        help="Kill all the jobs with a status")

    parser.add_argument('-f','--forever', action='store_true', 
                help="Write job.done so that it cannot be auto-started.")

    parser.add_argument('-u','--submit', action='store_true', 
                help="Kill and re-submit it.")

    args = parser.parse_args()
    
        
    # Qjob has idx, status, btime, server, slots, folder, str, short_str
    qjobs=mypy.Qjob_list()
    qjobs.myq_without_folder()
    print(qjobs.short_str())
    # print(qjobs)
    print('{} jobs in total'.format(qjobs.length()))
    print('='*30)


    print(args)

    if args.all:
        kill_all_jobs(qjobs,forever=args.forever,submit=args.submit)
    else:
        kill_some_jobs(qjobs,path=args.path,status=args.status,
                       forever=args.forever,submit=args.submit)
