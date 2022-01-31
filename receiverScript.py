import os
from datetime import datetime
from pysnmp.smi import builder, view, rfc1902

import configparser
userConfig = configparser.ConfigParser()
userConfig.read('envvars.txt')

# load mibs
mibBuilder = builder.MibBuilder()
mibSources = mibBuilder.getMibSources()
mibBuilder.setMibSources(*mibSources)
mibBuilder.loadModules('SNMPv2-MIB', 'SNMP-COMMUNITY-MIB')
mibViewController = view.MibViewController(mibBuilder)

from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.api import v2c

#Debug logging :
#from pysnmp import debug
#debug.setLogger(debug.Debug('all'))

filename="snmplistener.log.{}".format(datetime.now().strftime('%s'))

def writeLogs(stringToWrite):
	with open(filename,'a+') as f: 
		f.write(stringToWrite) 

purposeStr = 'SNMPv3 Trap Listener'
print(len(purposeStr) * '~' + '\n' + purposeStr + '\n' + len(purposeStr) * '~')
writeLogs('\n')
outstring='Starting {} @ {}'.format(purposeStr, datetime.now().strftime("%m/%d/%Y-%H:%M:%S.%f")[:-3])
writeLogs(len(outstring) * '~' + '\n' + outstring + '\n' + len(outstring) * '~')
print('Now listening for traps ...')


# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher

snmpEngine = engine.SnmpEngine()


# Transport setup
# UDP over IPv4
config.addTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpTransport().openServerMode(('0.0.0.0', 1161))
)

# SNMPv3/USM setup

config.addV3User(
    snmpEngine, userConfig['DEFAULT']['SNMPUSER'],
    config.usmHMAC128SHA224AuthProtocol, userConfig['DEFAULT']['SNMPAUTH'],
    config.usmAesCfb192Protocol, userConfig['DEFAULT']['SNMPPRIV'],
    securityEngineId=v2c.OctetString(hexValue='0102030405060708')
)


# Callback function for receiving notifications
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
	logTime=datetime.now().strftime("%m/%d/%Y-%H:%M:%S.%f")[:-3]
	writeLogs('\n\n{}\nNotification from ContextEngineId "{}", ContextName "{}"'.format(logTime,contextEngineId.prettyPrint(), contextName.prettyPrint()))
	print('\nNotification from ContextEngineId "%s", ContextName "%s"' % (contextEngineId.prettyPrint(),
																		contextName.prettyPrint()))

	varBinds = [rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolveWithMib(mibViewController) for x in varBinds]
	for varBind in varBinds:
		writeLogs('\n' + varBind.prettyPrint())
		print(varBind.prettyPrint())
	
	writeLogs('\n')


# Register SNMP Application at the SNMP engine
ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)  # this job would never finish

# Run I/O dispatcher which would receive queries and send confirmations
try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise
