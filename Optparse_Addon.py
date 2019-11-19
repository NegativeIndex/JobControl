#!/usr/bin/env python
"""
A little imporvement over the optparse module. 
"""

from optparse import (OptionParser,BadOptionError,AmbiguousOptionError)
import logging
import sys,subprocess,os,re
##############################
# a wrapped class which passes all unknown option to args
class PassThroughOptionParser(OptionParser):
    """
    An unknown option pass-through implementation of OptionParser.

    When unknown arguments are encountered, bundle with largs and try again,
    until rargs is depleted.  

    sys.exit(status) will still be called if a known argument is passed
    incorrectly (e.g. missing arguments or bad argument types, etc.) 

    Usage ::

        from optparse import (OptionParser,BadOptionError,AmbiguousOptionError)
        parser=PassThroughOptionParser(usage=usage,description=description)
        (opts,unk_args) = parser.parse_args(sargs)
    """
    def _process_args(self, largs, rargs, values):
        while rargs:
            try:
                OptionParser._process_args(self,largs,rargs,values)
            except (BadOptionError,AmbiguousOptionError) as e:
                largs.append(e.opt_str)

## convert long option with single dash to two dashes
def long_option_dash_1to2(args):
    """
    Change the sinlge-dash in front of a long option back to double-dash.
    """
    new_argv = []
    for arg in args:
        if arg.startswith('-') and len(arg) > 2:
            arg = '-' + arg
        new_argv.append(arg)
    return new_argv

# convert long option with two dashes to one
def long_option_dash_2to1(args):
    """
    Change the double-dash in front of a long option to single-dash.
    """
    new_argv = []
    for arg in args:
        arg = re.sub('^--','-',arg)
        new_argv.append(arg)
    return new_argv


#########################
# main function
def main(argv):
    """A main function to implement the enhanced optparse_addon
    function. The unknown options are passed to linux bash find
    function.

    """
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

    # add some options
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
    unk_args.pop(0)  # remove the first, command name
    logging.debug("Saved args are {}".format(sargs))
    logging.debug("Accepted options is {}".format(opts))
    logging.debug("Unkonwn args are {}".format(unk_args))

    # find all the folders which contains simulations
    comm=["find"]+unk_args+['-name',"job.info"]
    res = subprocess.check_output(comm).decode("ascii").rstrip()
    # logging.debug(res)
    jobfiles=res.split('\n')
    jobfiles=[os.path.abspath(jobfile) for jobfile in jobfiles 
              if len(jobfile.strip())>0]

    jobfiles.sort()
    for f in jobfiles:
        logging.debug(f)


#########################
# main function
if __name__=='__main__':
    main(sys.argv)
