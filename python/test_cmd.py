#!/usr/bin/env python2
"""
Python Command Line Interface to the pxar API.
"""
import PyPxarCore
from PyPxarCore import Pixel, PixelConfig, PyPxarCore, PyRegisterDictionary, PyProbeDictionary
from functools import wraps # used in parameter verification decorator
from numpy import set_printoptions, nan

import cmd      # for command interface and parsing
import os # for file system cmds
import sys

# set up the DAC and probe dictionaries
dacdict = PyRegisterDictionary()
probedict = PyProbeDictionary()

# "arity": decorator used for parameter parsing/verification on each cmd function call
# Usually, the cmd module only passes a single string ('line') with all parameters;
# this decorator divides and verifies the types of each parameter.
def arity(n, m, cs=[]): # n = min number of args, m = max number of args, cs = types
    def __temp1(f):
        @wraps(f) # makes sure the docstring of the orig. function is passed on
        def __temp2(self, text):
            ps = filter(lambda p: p, text.split(" "))
            if len(ps) < n:
                print "Error: this command needs %d arguments (%d given)" % (n, len(ps))
                return
            if len(ps) > m:
                print "Error: this command takes at most %d arguments (%d given)" % (m, len(ps))
                return
            # now verify the type
            try:
                ps = [ c(p) for c, p in zip(cs, ps) ]
            except ValueError as e:
                print "Error: '" + str(p) + "' does not have " + str(c)
                return
            f(self, *ps)
        return __temp2
    return __temp1

def get_possible_filename_completions(text):
    head, tail = os.path.split(text.strip())
    if head == "": #no head
        head = "."
    files = os.listdir(head)
    return [ f for f in files if f.startswith(tail) ]
 
def extract_full_argument(line, endidx):
    newstart = line.rfind(" ", 0, endidx)
    return line[newstart:endidx]

class PxarConfigFile:
    """ class that loads the old-style config files of psi46expert """
    def __init__(self, f):
        self.config = {}
        import shlex
        thisf = open(f)
        try:
            for line in thisf:
                if not line.startswith("--"):
                    parts = shlex.split(line)
                    if len(parts) == 2:
                        self.config[parts[0].lower()] = parts[1]
        finally:
            thisf.close()
    def show(self):
        print self.config
    def get(self, opt, default = None):
        if default:
            return self.config.get(opt.lower(),default)
        else:
            return self.config[opt.lower()]

class PxarParametersFile:
    """ class that loads the old-style parameters files of psi46expert """
    def __init__(self, f):
        self.config = {}
        import shlex
        thisf = open(f)
        try:
            for line in thisf:
                if not line.startswith("--"):
                    parts = shlex.split(line)
                    if len(parts) == 3:
                        # ignore the first part (index/line number)
                        self.config[parts[1].lower()] = parts[2]
        finally:
            thisf.close()
    def show(self):
        print self.config
    def get(self, opt, default = None):
        if default:
            return self.config.get(opt.lower(),default)
        else:
            return self.config[opt.lower()]
    def getAll(self):
        return self.config
    

class PxarCoreCmd(cmd.Cmd):
    """Simple command processor for the pxar core API."""
    fullOutput=False

    def __init__(self, api):
        cmd.Cmd.__init__(self)
        self.prompt = "pxar core =>> "
        self.intro  = "Welcome to the pxar core console!"  ## defaults to None
        self.api = api
    
    def do_EOF(self, line):
        """ clean exit when receiving EOF (Ctrl-D) """
        return True

    def do_switchFullOutput(self, line):
        """Switch between full and suppressed output of all pixels"""
        if self.fullOutput:
            set_printoptions(threshold=1000)
            self.fullOutput = False
        else:
            set_printoptions(threshold=nan)
            self.fullOutput = True

    @arity(0,0,[])
    def do_getVersion(self):
        """getVersion: returns the pxarcore library version"""
        print self.api.getVersion()
        
    def complete_getVersion(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_getVersion.__doc__, '']

    @arity(1,1,[str])
    def do_flashTB(self, filename):
        """flashTB [filename]: flash the DTB with new firmware"""
        self.api.flashTB(filename)
        
    def complete_flashTB(self, text, line, start_index, end_index):
        # tab-completion for the file path:
        try:
            # remove specific delimeters from the readline parser
            # to allow completion of filenames with dashes
            import readline
            delims = readline.get_completer_delims( )
            delims = delims.replace('-', '')
            readline.set_completer_delims(delims)
        except ImportError:
            pass
        return get_possible_filename_completions(extract_full_argument(line,end_index))

    @arity(0,0,[])
    def do_HVon(self):
        """HVon: switch High voltage for sensor bias on"""
        self.api.HVon()
        
    def complete_HVon(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_HVon.__doc__, '']

    @arity(0,0,[])
    def do_Poff(self):
        """Pon: switch DTB power output off"""
        self.api.Poff()
        
    def complete_Poff(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_Poff.__doc__, '']

    @arity(0,0,[])
    def do_Pon(self):
        """Pon: switch DTB power output on"""
        self.api.Pon()
        
    def complete_Pon(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_Pon.__doc__, '']

    @arity(0,0,[])
    def do_HVoff(self):
        """HVoff: switch High voltage for sensor bias off"""
        self.api.HVoff()
        
    def complete_HVoff(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_HVoff.__doc__, '']

    @arity(0,0,[])
    def do_getTBia(self):
        """getTBia: returns analog DTB current"""
        print "Analog Current: ", (self.api.getTBia()*1000), " mA"
        
    def complete_getTBia(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_getTBia.__doc__, '']

    @arity(0,0,[])
    def do_getTBva(self):
        """getTBva: returns analog DTB voltage"""
        print "Analog Voltage: ", self.api.getTBva(), " V"
        
    def complete_getTBva(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_getTBva.__doc__, '']

    @arity(0,0,[])
    def do_getTBid(self):
        """getTBid: returns digital DTB current"""
        print "Digital Current: ", (self.api.getTBid()*1000), " mA"
        
    def complete_getTBid(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_getTBid.__doc__, '']

    @arity(0,0,[])
    def do_getTBvd(self):
        """getTBvd: returns digital DTB voltage"""
        print "Digital Voltage: ", self.api.getTBvd(), " V"
        
    def complete_getTBvd(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_getTBvd.__doc__, '']

    @arity(0,2,[int, int])
    def do_getEfficiencyMap(self, flags = 0, nTriggers = 10):
        """getEfficiencyMap [flags = 0] [nTriggers = 10]: returns the efficiency map"""
        print self.api.getEfficiencyMap(flags,nTriggers)
        
    def complete_getEfficiencyMap(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_getEfficiencyMap.__doc__, '']

    @arity(0,2,[int, int])
    def do_getPulseheightMap(self, flags = 0, nTriggers = 10):
        """getPulseheightMap [flags = 0] [nTriggers = 10]: returns the pulseheight map"""
        print self.api.getPulseheightMap(flags,nTriggers)
        
    def complete_getPulseheightMap(self, text, line, start_index, end_index):
        # return help for the cmd
        return [self.do_getPulseheightMap.__doc__, '']

    @arity(1,3,[str, int, int])
    def do_getThresholdMap(self, dacname, dacstep = 1, ddacmin = 0, dacmax = 255, threshold = 50, flags = 0, nTriggers = 10):
        """getPulseheightMap [DAC name] [flags = 0] [nTriggers = 10]: returns the threshold map for the given DAC"""
        print self.api.getThresholdMap(dacname,1,0,255,50,flags,nTriggers)
        
    def complete_getThresholdMap(self, text, line, start_index, end_index):
        if text and len(line.split(" ")) <= 2: # first argument and started to type
            # list matching entries
            return [dac for dac in dacdict.getAllROCNames()
                        if dac.startswith(text)]
        else:
            if len(line.split(" ")) > 2:
                # return help for the cmd
                return [self.do_getThresholdMap.__doc__, '']
            else:
                # return all DACS
                return dacdict.getAllROCNames()

    @arity(2,2,[str, str])
    def do_SignalProbe(self, probe, name):
        """SignalProbe [probe] [name]: Switches DTB probe output [probe] to signal [name]"""
        self.api.SignalProbe(probe,name)

    def complete_SignalProbe(self, text, line, start_index, end_index):
        probes = ["d1","d2","a1","a2"]
        if len(line.split(" ")) <= 2: # first argument
            if text: # started to type
                # list matching entries
                return [pr for pr in probes
                        if pr.startswith(text)]
            else:
                # list all probes
                return probes
        elif len(line.split(" ")) <= 3: # second argument
            p = line.split(" ")[1:2]
            print 
            if text: # started to type
                if p.startswith("a"):
                    return [pr for pr in probedict.getAllAnalogNames()
                            if pr.startswith(text)]
                elif p.startswith("d"):
                    return [pr for pr in probedict.getAllDigitalNames()
                            if pr.startswith(text)]
                else:
                    return [self.do_SignalProbe.__doc__, '']
            else:
                # return all signals:
                if p.startswith("a"):
                    return probedict.getAllAnalogNames()
                elif p.startswith("d"):
                    return probedict.getAllDigitalNames()
                else:
                    return [self.do_SignalProbe.__doc__, '']
        else:
            # return help for the cmd
            return [self.do_SignalProbe.__doc__, '']

    @arity(2,3,[str, int, int])
    def do_setDAC(self, dacname, value, rocid = None):
        """setDAC [DAC name] [value] [ROCID]: Set the DAC to given value for given roc ID"""
        self.api.setDAC(dacname, value, rocid)

    def complete_setDAC(self, text, line, start_index, end_index):
        if text and len(line.split(" ")) <= 2: # first argument and started to type
            # list matching entries
            return [dac for dac in dacdict.getAllROCNames()
                        if dac.startswith(text)]
        else:
            if len(line.split(" ")) > 2:
                # return help for the cmd
                return [self.do_setDAC.__doc__, '']
            else:
                # return all DACS
                return dacdict.getAllROCNames()

    @arity(1,1,[str])
    def do_getDACRange(self, dacname):
        """getDACRange [DAC name]: Get the valid value range for the given DAC"""
        print "DAC ", dacname, ": 0 -", self.api.getDACRange(dacname)

    def complete_getDACRange(self, text, line, start_index, end_index):
        if text and len(line.split(" ")) <= 2: # first argument and started to type
            # list matching entries
            return [dac for dac in dacdict.getAllROCNames()
                        if dac.startswith(text)]
        else:
            if len(line.split(" ")) > 2:
                # return help for the cmd
                return [self.do_getDACRange.__doc__, '']
            else:
                # return all DACS
                return dacdict.getAllROCNames()

    def do_quit(self, arg):
        """quit: terminates the application"""
        sys.exit(1)

    # shortcuts
    do_q = do_quit

def main(argv=None):
    if argv is None:
        argv = sys.argv
        progName = os.path.basename(argv.pop(0))

    print argv
    # command line argument parsing
    import argparse
    parser = argparse.ArgumentParser(prog=progName, description="A Simple Command Line Interface to the pxar API.")
    parser.add_argument('--dir', '-d', metavar="DIR", help="The directory with all required config files.")
    parser.add_argument('--verbosity', '-v', metavar="LEVEL", default="INFO", help="The output verbosity set in the pxar API.")
    args = parser.parse_args(argv)

    if not args.dir or not os.path.isdir(args.dir):
        print "Error: no or invalid configuration directory specified!"
        sys.exit(100)
    
    config = PxarConfigFile('%sconfigParameters.dat'%(os.path.join(args.dir,"")))
    tbparameters = PxarParametersFile('%s%s'%(os.path.join(args.dir,""),config.get("tbParameters")))
    tbmparameters = PxarParametersFile('%s%s'%(os.path.join(args.dir,""),config.get("tbmParameters")))
    # Power settings:
    power_settings = {
        "va":config.get("va",1.9),
        "vd":config.get("vd",2.6),
        "ia":config.get("ia",1.190),
        "id":config.get("id",1.10)}

    # Pattern Generator for single ROC operation:
    pg_setup = (
        ("PG_RESR",25),  
        ("PG_CAL",101+5),
        ("PG_TRG",16),   
        ("PG_TOK",0))    
    

    # Start an API instance from the core pxar library
    api = PyPxarCore(usbId=config.get("testboardName"),logLevel=args.verbosity)
    print api.getVersion()
    if not api.initTestboard(pg_setup = pg_setup, 
                             power_settings = power_settings,
                             sig_delays = tbparameters.getAll()):
        print "WARNING: could not init DTB -- possible firmware mismatch."
        print "Please check if a new FW version is available"
        exit

    
    tbmDACs = []
    for tbm in range(int(config.get("nTbms"))):
        tbmDACs.append(tbmparameters.getAll())

    print "Have DAC config for " + str(len(tbmDACs)) + " TBMs:"
    for idx, tbmDAC in enumerate(tbmDACs):
        for key in tbmDAC:
            print "  TBM dac: " + str(key) + " = " + str(tbmDAC[key])

    # init pixel list
    pixels = list()
    for column in range(0, 51):
        for row in range(0, 79):
            p = PixelConfig(column,row,15)
            p.mask = False
            pixels.append(p)

    rocDacs = []
    rocPixels = list()
    for roc in xrange(int(config.get("nrocs"))):
        dacconfig = PxarParametersFile('%s%s_C%i.dat'%(os.path.join(args.dir,""),config.get("dacParameters"),roc))
        rocDacs.append(dacconfig.getAll())
        rocPixels.append(pixels)

    print "And we have just initialized " + str(len(pixels)) + " pixel configs to be used for every ROC!"
            
    api.initDUT(0,config.get("tbmType","tbm08"),tbmDACs,config.get("rocType"),rocDacs,rocPixels)

    api.testAllPixels(True)
    print " enabled all pixels"

    # start the cmd line and wait for user interaction
    PxarCoreCmd(api).cmdloop()



if __name__ == "__main__":
    sys.exit(main())
