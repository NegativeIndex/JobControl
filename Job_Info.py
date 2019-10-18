#!/usr/bin/env python
"""
Define a class the process job event and job.info files
"""
import sys
import subprocess
import datetime,time
import re
import os,glob
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
        string="{}, status='{}', {}".format(self.id,self.status,tt)
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
    """A class describes one fb file """
    pass

class FB_Files(object):
    """A class includes several fb files """
    pass


#########################
class Simulation(object):
    """A simulation is a folder with a job.info file and several fb
    files. This is the class combining the information from job.info
    and fb files.

    Attibutes: 

        events is an object of JobEvents

        fbfiles is an object of FB_Files
    
        status: 'f' (finished), 'a' (active) or 'd' (dead). 'f' comes
        from the JobEvents. 'a' and 'd' are from FB_Files.

        time: time in seconds used to finish a job; time used by an
        active job upto now; the longest time used by a dead job.
    """
    pass
                

#########################
# main function
def main(argv):
    """
    Use the main function for debug
    """
    # logger
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(message)s')

    # test
    simulation=JobEvents.from_jobinfo('job.info')
    for e in simulation.events:
        logging.debug(e)
    dt=simulation.time_to_finish()
    logging.debug(dt)


#########################
# main function
if __name__=='__main__':
    main(sys.argv)
