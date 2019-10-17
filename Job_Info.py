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
    """A class to describe a series of job events in a folder related to
    a simulation.

    Attibutes: events, which is a list of JobEvent
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
        generate a JobEvents object from job.info file
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

    def is_finished(self):
        """The simulation is considered finished if there is one 'e' event in
        the events list
        """
        for e in self.events:
            if e.status=='e':
                return True
        return False

    def time_to_finish(self):
        """Calculate the longest time used to finish the simulation in seconds
        if the simulaiton is finished properly. Otherwise return None
        """
        endjobs=[e for e in self.events if e.status=='e']
        for e in endjobs:
            pass
        return None
   

                

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
    simulation.time_to_finish()


#########################
# main function
if __name__=='__main__':
    main(sys.argv)
