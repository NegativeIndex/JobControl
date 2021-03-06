#!/usr/bin/env python

"""Define two classes: Qjob and Qjob_list to collect information from
qstat command. The Qjob_list class has all the information about the
submitted jobs.

"""
import sys
import subprocess
import datetime 
import re
import os,glob,time
import random

##################################################
# define a class to collect information from qstat
###################################################
class Qjob:
    """ The Qjob class describe one submitted job.  

    It has 6 abbtributes.

        idx: job id

        status: 'r' (run), 'w' (wait)
    
        server: the submitted queue, UI, all.q, INFORMATICS

        slots: the number of CPU used

        folder: the job working folder

    """
    def __init__(self,idx,status,btime,server,slots,folder=None):
        self.idx = idx
        self.status = status 
        self.btime=btime
        self.server=server
        self.slots=slots
        self.folder=folder

    def __str__(self):
        ss="{:>7} {:>3} {:>6}   {:20} {:2}\n{}".format(
            self.idx,self.status,self.server,
            self.btime.strftime("%m/%d/%Y %H:%M:%S"),
            self.slots,
            self.folder)
        return  ss     

    def short_str(self):
        '''A short string to describe the job'''
        ss="{:>7} {:>3} {:>6}   {:20} {:2}".format(
            self.idx,self.status,self.server,
            self.btime.strftime("%m/%d/%Y %H:%M:%S"),
            self.slots)
        return  ss     

    # update the folder of a job
    def get_folder(self):
        '''Get the job folder is slow and complex. Use this function only when
        it is necessary.

        '''
        idx=self.idx
        try:
            res = subprocess.check_output(['qstat','-j',idx])
            match=re.search(r'sge_o_workdir:\s+(\S+)\s+',
                            res.decode("utf-8"))
            if match:
                self.folder=match.group(1)
            else:
                self.folder=None
        except subprocess.CalledProcessError as e:
            self.folder=None

#############################
class Qjob_list:
    """The Qjob_list class has a abbtributes, qjobs, which is a list of
    Qjob. The class is iterable.

    """
    def __init__(self,qjobs=[]):
        self.qjobs=qjobs
        
    def __str__(self):
        ss=""
        for qjob in self.qjobs:
            ss=ss+str(qjob)+"\n"
        return ss.rstrip()

    def __iter__(self):
        self.pter = 0
        return self

    def __next__(self):
        if self.pter < len(self.qjobs):
            self.pter += 1
            return self.qjobs[self.pter-1]
        else:
            raise StopIteration

    def length(self):
        """Return the number of jobs in the class"""
        if self.qjobs:
            return len(self.qjobs)
        else:
            return 0

    def short_str(self):
        """Return a short strig for the class"""
        ss=""
        for qjob in self.qjobs:
            ss=ss+qjob.short_str()+"\n"
        return ss.rstrip()

    def append(self,qjob):
        """Add a Qjob to the class"""
        self.qjobs.append(qjob)
        
    # check the status giving idx
    def checkstatus(self,idx):
        """Check job staus using job id. If the job is not found, the stauts
        is 'n'."""
        for job in self.qjobs:
            if idx==job.idx: return job.status
        return "n"

    # find a job based on idx    
    def find(self,idx):
        """Find a job based on the job id. Return None if not found. I assume
        the jobs cannot have the same id."""
        for job in self.qjobs:
            if idx==job.idx:  return job
        return None
        
    # find a job based on the folder
    def find_base_folder(self,folder):
        jobs_list=[job for job in self.qjobs if 
                   job.folder is not None and 
                   os.path.abspath(job.folder)==os.path.abspath(folder)]
        return jobs_list

    # update itself based on myq results
    # don't update folder to save time
    def myq_without_folder(self):
        """Update the class with myq command. Don't collect the folder
        information to save time.

        Code examples::

            qjobs=Qstat_Class.Qjob_list()
            qjobs.myq_without_folder()
            qjobs.get_folders()

        Or ::

            qjobs=Qstat_Class.Qjob_list()
            qjobs.myq()

        """
        self.qjobs=[]

        res=subprocess.check_output("myq").decode("utf-8")
        lines=res.splitlines()
        line0=lines[0]
        del lines[0:2]
        vars=('job-ID','prior','name','user','state', 
              'submit/start at','queue', 'slots ja-task-ID')
        bnd=[re.search(var,line0).start(0) for var in vars]
        bnd.append(0)
        dict={'idx':0,'status':4,'btime':5,'queue':6,'slots':7}

        for line in lines:
            bnd[-1]=len(line)
            n=dict['idx']
            idx=line[bnd[n]:bnd[n+1]].rstrip().lstrip()
            n=dict['status']
            status=line[bnd[n]:bnd[n+1]].rstrip().lstrip()
            n=dict['btime']
            btime_str=line[bnd[n]:bnd[n+1]].rstrip().lstrip()
            n=dict['queue']
            queue=line[bnd[n]:bnd[n+1]].rstrip().lstrip()
            n=dict['slots']
            slots=line[bnd[n]:bnd[n+1]].rstrip().lstrip()

            btime=datetime.datetime.strptime(btime_str, "%m/%d/%Y %H:%M:%S")
            matchObj = re.match( r'(.*)@', queue, re.M|re.I)
            if matchObj:
                server=matchObj.group(1)
            else:
                server="all.q"
            
            qjob=Qjob(idx,status,btime,server,slots,folder=None)
            self.append(qjob)


    def get_folders(self):
        """Update the folder informaiton of the whole list"""
        for job in self.qjobs:
            job.get_folder()

    # update itself based on myq results
    def myq(self):
       """
       Update the class with myq command. It equivalent::

           qjobs.myq_without_folder()
           qjobs.get_folders()

       """
       self.myq_without_folder()
       self.get_folders()

##################################################
# actions
###################################################
def kill_job(idx):
    """Kill a job based on job id. Then wait 3 seconds"""
    comm=["qdel",idx]
    res = subprocess.check_output(comm).decode("ascii").rstrip()
    print("Killing message: "+res)
    time.sleep(3)


# def kill_job(job, restart=True):
#     idx=job.idx
#     comm=["qdel",idx]
#     try: 
#         res = subprocess.check_output(comm).decode("ascii").rstrip()
#         print("Killing message: "+res)
#         time.sleep(3)
#     except subprocess.CalledProcessError as e:
#         print("qdel error:\n" + e.output)
 
#     # if restart is False, I have to write the job.done file
#     if not restart:
#         cwd=os.getcwd()
#         os.chdir(job.folder)
#         print("Write to job.done and job.info")
#         with open('job.done','a') as f:
#             f.write('-'*29+'\n')
#             comm=["date",]
#             res = subprocess.check_output(comm).decode("ascii").rstrip()
#             f.write(res+'\n')
#             f.write('{} killed in the middle\n'.format(job.idx))
#         with open('job.info','a') as f:
#             f.write('-'*29+'\n')
#             comm=["date",]
#             res = subprocess.check_output(comm).decode("ascii").rstrip()
#             f.write(res+'\n')
#             f.write('{} killed in the middle\n'.format(job.idx))

#         os.chdir(cwd)


# ##############################
# # replace strings in a file
# ##############################
# def file_re_sub(fname1,fname2,*argv):
#     with open(fname1, "rt") as fin:
#         fin=open(fname1, 'rt')
#         lines=fin.readlines()
#         fin.close()

#         for i,line in enumerate(lines):
#             for pair in argv:
#                 line=re.sub(pair[0],pair[1],line)
#             lines[i]=line

#         fout=open(fname2, 'wt')
#         fout.write("".join(lines))
#         fout.close()

        
# ####################################
# def submit_job(path='./',server="all.q"):
#     cwd = os.getcwd()
#     os.chdir(path)
#     print(path)
#     files= glob.glob("dwt*.job")
#     for fname in  files:
#         comm1=["-q", server]
#         try: 
#             res=subprocess.check_output(["qsub"]+comm1+[fname])
#             line=res.decode("utf-8")
#             print(line)
#             with open("job.begin", "a+") as f:
#                 f.write(line)
#         except subprocess.CalledProcessError as e:
#             errno, strerror = e.args
#             print("Error({}): {}".format(errno,strerror))
#     os.chdir(cwd)
        
    
# ####################################    
# def mkjob_mpi(pyname,path='./',smp=2,cpu=None):
#     # cpu can be 128G, 192G, 256G or 512G
#     path=os.getcwd()
#     os.chdir(path)
#     try:
#         subprocess.call(["mkjob-mpi-all",pyname])
#         jobname=re.sub(r'(\w+).py',r'dwt-\1.job',pyname)
#         file_re_sub(jobname,jobname,
#                        (r'-pe\s+smp.*$','-pe smp {:d}'.format(smp)),
#                        (r'mpirun -np\s+\d+','mpirun -np {:d}'.format(smp)))
#         if cpu:
#             file_re_sub(jobname,jobname,
#                            (r'-l\s+\d+G=true','-l {}=true'.format(cpu)))
#             print('{:d} {} CPU are used'.format(smp, cpu))
#         else:
#             file_re_sub(jobname,jobname,
#                            (r'#\$ -l \d+G=true\s+',''))
#             print('{:d} any CPU are used'.format(smp))
#     except subprocess.CalledProcessError as e:
#         errno, strerror = e.args
#         print("Error({}): {}".format(errno,strerror))
#         os.chdir(path)
#     os.chdir(path)




