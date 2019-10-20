#!/usr/bin/env python
"""
Define a class the process job event and job.info files
"""
import sys
import subprocess
import datetime,time
import re
import os,glob
from pathlib import Path
import logging

####################
class JobEvent(object):
    """
    A class to describe job begin and job end.

    Attibutes: id, status, time.

      id is a digit string;  

      status is 'begin',  'end' or 'bad' (end badly); 

      time is a time.struct_time object.
    """
    def __init__(self,id=None,status=None,time=None):
        self.id=id
        self.status=status
        self.time=time

    def __str__(self):
        tt=time.strftime("%Y-%m-%d %H:%M:%S", self.time)
        string="Job event: {}, status='{}', {}".format(self.id,self.status,tt)
        return string

#####################
class JobEvents(object):
    """A class to describe a job.info file with several job events
 
    """
    def __init__(self,events=[]):
        self.events=events

    def __str__(self):
        ss=''
        for e in self.events:
            ss+=str(e)+'\n'
        return ss.rstrip()

    def __iter__(self):
        self.pter = 0
        return self

    def __next__(self):
        if self.pter < len(self.events):
            self.pter += 1
            return self.events[self.pter-1]
        else:
            raise StopIteration

    @classmethod
    def from_jobinfo(cls,jobfile):
        """
        generate a JobEvents object from a job.info file
        """
        events=[]
        with open(jobfile, 'r') as f:
            mfile=f.readlines()

        for line in mfile:
            line=line.rstrip()
            # logging.debug(line)
            # first line
            if re.search('^\+',line):
                status='begin'
            if re.search('^-----------',line):
                status='end'
            # second line
            try:
                tt=time.strptime(line,"%a %b %d %H:%M:%S %Z %Y")
                # tt=time.mktime(tt)
            except ValueError:
                pass
            # third line
            mobj=re.search('^[0-9]+',line)
            if mobj:
                id=mobj.group()
                if not re.search('^[0-9]+ dwt',line):
                    status='bad'
                event=JobEvent(id,status,tt)
                events.append(event)
        return cls(events)

    def time_to_finish(self):
        """Calculate the latest time used to finish the simulation in seconds
        if the simulaiton is finished properly. Otherwise return None

        """
        try: 
            endjobs=[e for e in self.events if e.status=='end']
            assert len(endjobs)>0 
            e1=endjobs[-1]
            beginjobs=[e for e in self.events
                       if e.status=='begin' and e.id==e1.id]
            assert len(beginjobs)>0 
            e0=beginjobs[-1]
            dt=time.mktime(e1.time)-time.mktime(e0.time)
            return dt
        except AssertionError:
            return None
   
#######################
class FB_File(object):
    """A class describes one fb file. FB file is generally a very long
    file. I don't want to read it.

    Attibutes: id, status, time.

        id is a digit string;  
    
        status is 'active' or 'dead'; 

        time is a time.struct_time object which shows the last updated time

        size is the file size

    """
    def __init__(self,id=None,status=None,time=None,size=None):
        self.id=id
        self.status=status
        self.time=time
        self.size=size

    def __str__(self):
        tt=time.strftime("%Y-%m-%d %H:%M:%S", self.time)
        string="FB file: {}, status='{}',size={:s}, {}".format(
            self.id,self.status,self.size_str(self.size),tt)
        return string

    @staticmethod
    def size_str(n):
        """convert a number to a good string"""
        if n>1e9:
            ss='{:0.2f}GB'.format(n/1e9)
        elif n>1e6:
            ss='{:0.2f}MB'.format(n/1e6)
        elif n>1e3:
            ss='{:0.2f}KB'.format(n/1e3)
        else:
            ss='{:d}B'.format(n)
        return ss

    @classmethod
    def from_file(cls,fb_file):
        """Process a fb file to a FB_File object"""
        try:
            fname=os.path.basename(fb_file)
            # logging.debug(fname)
            # id
            mobj=re.search('([0-9]+)\.txt',fname)
            assert mobj
            id=mobj.group(1)
            # logging.debug(id)
            # modification time, seconds since the epoch
            mtime=os.path.getmtime(fname) 
            # status
            now=time.time()
            if now-mtime<10*60: # 10 minute
                status='active'
            else:
                status='dead'
            # size
            size=os.path.getsize(fname)
            return cls(id,status,time.gmtime(mtime),size)

        except AssertionError:
            return cls(None,None,None)


class FB_Files(object):
    """    A class includes several fb files. It has an attribute fb_files. It
    is iterable."""

    def __init__(self,fb_files=[]):
        self.fb_files=fb_files

    def __str__(self):
        ss=''
        for f in self.fb_files:
            ss+=str(f)+'\n'
        return ss.rstrip()

    def __iter__(self):
        self.pter = 0
        return self

    def __next__(self):
        if self.pter < len(self.fb_files):
            self.pter += 1
            return self.fb_files[self.pter-1]
        else:
            raise StopIteration

    @classmethod
    def from_folder(cls,folder):
        """Find fb files in a folder and process them"""
        files=glob.glob('fb*.txt')
        fbs=[FB_File.from_file(f) for f in files]
        return cls(fb_files=fbs)

#########################
class Simulation(object):
    """A simulation is a folder with a job.info file and several fb
    files. This is the class combining the information from job.info
    and fb files.

    Attibutes: 
    
        folder is where the simulation lives

        events is an object of JobEvents

        fbfiles is an object of FB_Files
    
        status: 'finished', 'active', 'dead' or 'abnormal. 'finished' comes
        from the JobEvents; other statuses come from FB_Files.

        time: time in seconds used to finish a job; time used by an
        active job upto now; the longest time used by a dead job.
    
        message: a string to describe the situation
    """
    def __init__(self,folder=None,events=None,fbfiles=None,
                 status=None,time=None,message=None):
        self.folder=folder
        self.events=events
        self.fbfiles=fbfiles
        self.status=status
        self.time=time
        self.message=message

    def __str__(self):
        ss1='Simulation in {}'.format(self.folder)
        ss2='status={}, time={:0.2f} hours'.format(self.status,
                                                   self.time/3600)
        ss3='{}'.format(self.message)
        return ss1+'\n'+ss2+'\n'+ss3

    @classmethod
    def from_jobinfo(cls,jobinfo):
        """Build the Simulation object from the job.info file and the folder
        with the job file. This is a major function doing most of the
        jobs

        """
        # process events
        f=os.path.abspath(jobinfo)
        p=Path(f)
        folder=str(p.parent)
        # logging.debug(folder)
        events=JobEvents.from_jobinfo(jobinfo)
        files=FB_Files.from_folder(folder)
        
        # get the simulation information based on events 
        utime=events.time_to_finish()
        # if simulation was finished
        if utime is not None:
            status='finished'
            message='Simulation was finished'
            return cls(folder,events=events,fbfiles=files,
                       status=status,time=utime,message=message)

        # if simulation not done
        try:
            if len(files.fb_files)==0:
                status='empty'
                message='The folder has no fb files'
                return cls(folder,events=events,fbfiles=files,
                           status=status,time=None,message=message)

            active_files=[f for f in files if f.status=='active']
            if len(active_files)==0:
                status='dead'
                message='The simulation is dead and unfinished'
                bigf=max(files, key=lambda f: f.size)
                # logging.debug(bigf)
                
            elif len(active_files)>1:
                status='abnormal'
                message='There are {} active jobs'.format(len(active_files))
                bigf=max(active_files, key=lambda f: f.size)
            else:
                status='active'
                message='The simulation is active'
                bigf=max(active_files, key=lambda f: f.size)

            bevent=[e for e in events if e.id==bigf.id]
            # logging.debug(bevent[0])
            assert bevent
            utime=time.mktime(bigf.time)-time.mktime(bevent[-1].time)
            return cls(folder,events=events,fbfiles=files,
                       status=status,time=utime,message=message)
        except AssertionError:
            return cls(folder,events=events,fbfiles=files,
                       status=status,time=None,message=message)
        

#########################
# main function
def main(argv):
    """
    Use the main function for debug
    """
    # logger
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(message)s')

    # test fb classes
    # fb_files=FB_Files.from_folder('f./')
    # logging.debug(fb_files)

    # test simulation class
    sim=Simulation.from_jobinfo('job.info')
    logging.debug(sim)

    # test Simulation class
    # simulation=Simulation.from_jobinfo('job.info')
    # logging.debug(simulation)
    # for e in simulation.events:
    #     logging.debug(e)
    # dt=simulation.time_to_finish()
    # logging.debug(dt)


#########################
# main function
if __name__=='__main__':
    main(sys.argv)
