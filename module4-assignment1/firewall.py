'''
Coursera:
- Software Defined Networking (SDN) course
-- Module 4 Programming Assignment

Professor: Nick Feamster
Teaching Assistant: Muhammad Shahbaz

Created by: Vitaliy Ivanov
'''

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
''' Add your imports here ... '''
import csv

log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]

''' Add your global variables here ... '''

class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")
        # Our firewall table
        self.firewall = {}

    def sendRule (self, src, dst, duration = 0):
        """
        Drops this packet and optionally installs a flow to continue
        dropping similar ones for a while
        """
        if not isinstance(duration, tuple):
            duration = (duration,duration)
        msg = of.ofp_flow_mod()
        match = of.ofp_match()
        match.dl_src = EthAddr(src)
        match.dl_dst = EthAddr(dst)
        msg.match = match
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.priority = 10
        self.connection.send(msg)

    # function that allows adding firewall rules into the firewall table
    def AddRule (self, src=0, dst=0, value=True):
        if (src, dst) in self.firewall:
            log.debug("Rule already present drop: src %s - dst %s", src, dst)
        else:
            log.debug("Adding firewall rule drop: src %s - dst %s", src, dst)
            self.firewall[(src, dst)]=value
            self.sendRule(src, dst, 10000)

    # function that allows deleting firewall rules from the firewall table
    def DeleteRule (self, src=0, dst=0):
        try:
            del self.firewall[(src, dst)]
            sendRule(src, dst, 0)
            log.debug("Deleting firewall rule drop: src %s - dst %s", src, dst)
        except KeyError:
            log.error("Cannot find in rule drop src %s - dst %s", src, dst)

    def _handle_ConnectionUp (self, event):
        ''' Add your logic here ... '''
        self.connection = event.connection

        ifile  = open(policyFile, "rb")
        reader = csv.reader(ifile)
        rownum = 0
        for row in reader:
            # Save header row.
            if rownum == 0:
                header = row
            else:
                colnum = 0
                for col in row:
                    #print '%-8s: %s' % (header[colnum], col)
                    colnum += 1
                self.AddRule(row[1], row[2])
            rownum += 1
        ifile.close()

        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)
