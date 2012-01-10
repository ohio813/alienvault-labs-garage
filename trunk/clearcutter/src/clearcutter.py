#!/usr/bin/env python

'''ClearCutter - a general purpose log analysis tool with OSSIM-specific features'''

__author__ = "CP Constantine"
__email__ = "conrad@alienvault.com"
__copyright__ = 'Alienvault 2012'
__credits__ = ["Conrad Constantine","Dominique Karg"]
__version__ = "0.1"
__license__ = "GPL"
__status__ = "Prototype"
__maintainer__ = "CP Constantine"

import sys,os,argparse,clusters,ccregex,progressbar


class LogFile(object):
    '''
    Log File object with a few helper functions for other clearcutter modes
    '''    
    _filedata = ""
    Filename = ""
    Length = 0
    Position = 0
    
    def __init__(self, filename, verbose=False):
        self.Filename = filename
        try:             
            if verbose == True : print "Using File: " + filename
            self._filedata = open(filename,'r')
        except ValueError:
            if verbose == True : print "Invalid Filename: " + sys.exc_info()[2]
            raise sys.exc_info()
        except IOError:
            if verbose == True : print "File Access Error: " + sys.exc_info()[2]
            raise sys.exc_info()
        self.Length = os.path.getsize(filename)
        
    def RetrieveCurrentLine(self, verbose=False ):
        self.Position = self._filedata.tell()        
        return self._filedata.readline()
        
def DoLogExtract(args):
    """Commence Log Message Extraction mode""" 
    try:
        log = LogFile(args.logfile)
    except IOError:
        print "File: " + log.Filename + " cannot be opened : " + str(sys.exc_info()[1])
        sys.exit()
    if args.v > 0 : print "Processing Log File "  + log.Filename + ":" + str(log.Length) + " bytes" 
    myclusters = clusters.ClusterGroup()
    logline = log.RetrieveCurrentLine() 
    widgets = ['Processing potential messages: ', progressbar.Percentage(), ' ', progressbar.Bar(marker=progressbar.RotatingMarker()),' ', progressbar.ETA()]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=100).start()
    while logline != "": #TODO: Make this actually exit on EOF
        myclusters.IsMatch(logline)
        pbar.update((1.0 * log.Position / log.Length) * 100)
        logline = log.RetrieveCurrentLine()
        
    pbar.finish()
    myclusters.Results()

    
def DoLogParse(args):
    """Commence Plugin Parsing Mode"""
    try:
        log = LogFile(args.logfile)
    except IOError:
        print "File: " + log.Filename + " cannot be opened : " + str(sys.exc_info()[1])
        sys.exit()
    myregexps = ccregex.ParsePlugin(args)
    myregexps.Parse()
    #import logregex
    #process log from plugin
    print "Not Yet Implemented"
    sys.exit()

def DoLogProfile():
    """Commence OSSIM SID Profiling"""
    # Prep Profiling
    # Do the regular logparse
    # Process and print the results
    print "Not Yet Implemented"
    sys.exit()


#=========================1
#Map Arg Modes to Launch functions
mode = {'identify' : DoLogExtract, 'parse' : DoLogParse, 'profile' : DoLogProfile} 
        
def ParseArgs():
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, \
                                     description='Processes log files for SIEM consumption',
                                     epilog='examples:\n\t%(prog)s identify sample.log\n\t%(prog)s parse plugin.cfg sample.log\n\t%(prog)s profile plugin.cfg sample.log')
    modeparsers = parser.add_subparsers(help='Command Mode Help')
           
    identifyparser = modeparsers.add_parser('identify',help='Log Event Candidate Identification')
    identifyparser.set_defaults(mode='identify') 
    identifyparser.add_argument(dest='logfile', action='store', type=str, help='log file to process')
    identifyparser.add_argument('-t', action='store', type=int, help='Threshold value for Variable Assignment', )
    identifyparser.add_argument('-v', action='count',help='verbose mode - use multiple times to increase verbosity')
    identifyparser.add_argument('-q', action='store_true',help='quiet mode - print nothing but results')
    identifyparser.add_argument('-o', action='store', type = str, metavar = 'file' , help='Write results to <file>')
    
    
    pluginparser = modeparsers.add_parser('parse',help = 'OSSIM Plugin Parse Testing')
    pluginparser.set_defaults(mode='parse')
    pluginparser.add_argument(dest='plugin', action='store', type=str,help='OSSIM plugin .cfg file')
    pluginparser.add_argument('-n', action='store', type=int, help='Show Matching values from position N')    
    pluginparser.add_argument('-v', action='count',help='verbose mode - use multiple times to increase verbosity')
    pluginparser.add_argument('-q', action='store_true',help='quiet mode - print nothing but results')
    pluginparser.add_argument('-o', action='store', type = str, metavar = 'file' , help='Write results to <file>')
    
    
    profileparser = modeparsers.add_parser('profile',help = 'OSSIM Plugin Performance Profiling')
    profileparser.set_defaults(mode='profile')
    profileparser.add_argument('plugin', action='store', type=str,help='OSSIM plugin .cfg file')
    profileparser.add_argument('-s','--sort', action='store_true',help='Sort Results by Execution Time')
    profileparser.add_argument('-v', action='count',help='verbose mode - use multiple times to increase verbosity')
    profileparser.add_argument('-q', action='store_true',help='quiet mode - print nothing but results')
    profileparser.add_argument('-o', action='store', type = str, metavar = 'file' , help='Write results to <file>')
    
    globalargs = parser.parse_args()
    
    mode[globalargs.mode](globalargs)

if __name__ == '__main__':
    ParseArgs()

