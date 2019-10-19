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

      status is 'b'(begin) or 'e' (end well) and 's' (end badly); 

      time is a time.struct_time object.
    """
    def __init__(self,id=None,status=None,time=None):
        self.id=id
        self.status=status
        self.time=time

    def __str__(self):
        tt=time.strftime("%Y-%m-%d %H:%M:%S", self.time)
        string="Job event {}, status='{}', {}".format(self.id,self.status,tt)
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
                status='b'
            if re.search('^-----------',line):
                status='e'
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
                    status='s'
                event=JobEvent(id,status,tt)
                events.append(event)
        return cls(events)

    def time_to_finish(self):
        """Calculate the latest time used to finish the simulation in seconds
        if the simulaiton is finished properly. Otherwise return None

        """
        try: 
            endjobs=[e for e in self.events if e.status=='e']
            assert len(endjobs)>0 
            e1=endjobs[-1]
            beginjobs=[e for e in self.events
                       if e.status=='b' and e.id==e1.id]
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
    
        status is 'a' (active) and 'd' (dead, end badly); 

        time is a time.struct_time object which shows the last updated time

    """
    def __init__(self,id=None,status=None,time=None):
        self.id=id
        self.status=status
        self.time=time

    def __str__(self):
        tt=time.strftime("%Y-%m-%d %H:%M:%S", self.time)
        string="fb file {}, status='{}', {}".format(self.id,self.status,tt)
        return string

    @classmethod
    def from_file(cls,fb_file):
        """Process a fb file to a FB_File object"""
        fname=os.path.basename(fb_file)
        logging.debug(fname)
        mobj=re.search('([0-9]+)\.txt',fname)
        if mobj:
            id=mobj.group(1)
            logging.debug(id)
        return cls(None,None,None)


class FB_Files(object):
    """A class includes several fb files """
    def __init__(self,fb_files=[]):
        self.fb_files=fb_files

    def __str__(self):
        ss=''
        for f in self.fb_files:
            ss+=str(e)+'\n'
        return ss.rstrip()

    @classmethod
    def from_folder(cls,folder):
        """Find fb files in a folder and process them"""
        pass

#########################
class Simulation(object):
    """A simulation is a folder with a job.info file and several fb
    files. This is the class combining the information from job.info
    and fb files.

    Attibutes: 
    
        folder is where the simulation lives

        events is an object of JobEvents

        fbfiles is an object of FB_Files
    
        status: 'f' (finished), 'a' (active) or 'd' (dead). 'f' comes
        from the JobEvents. 'a' and 'd' are from FB_Files.

        time: time in seconds used to finish a job; time used by an
        active job upto now; the longest time used by a dead job.
    """
    def __init__(self,folder=None,
                 events=None,fbfiles=None,status=None,time=None):
        self.folder=folder
        self.events=events
        self.fbfiles=fbfiles
        self.status=status
        self.time=time

    def __str__(self):
        ss='{}\nstatus={}, time={:0.2f} hours'.format(self.folder,
                                                      self.status,
                                                      self.time)
        return ss

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
        time=events.time_to_finish()
        if time is not None:
            status='f'
        else:
            status=None
        return cls(folder,events=events,fbfiles=None,
                   status=status,time=time)
        
        

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
    fb_file=FB_File.from_file('fb-rad-6596116.txt')


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
