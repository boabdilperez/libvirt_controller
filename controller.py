import libvirt
import sys
from xml.dom import minidom

DNAME = 'alpine-test2'
CONNSTRING = 'qemu:///system'


def list_all_domains(conn):
    '''Takes in a connection object for qemu and returns a list of all active and inactive domain names'''
    domain_names = conn.listDefinedDomains()
    if conn == None:
        print('Failed to get a list of domain names', file=sys.stderr)
    
    domain_ids = conn.listDomainsID()
    if domain_ids == None:
        print('Failed to get a list of domain IDs', file=sys.stderr)
    
    if len(domain_ids) != 0:
        for domain_id in domain_ids:
            domain = conn.lookupByID(domain_id)
            domain_names.append(domain.name())
    
    return domain_names


def list_active_domains(conn):
    '''Takes in a qemu connection object and returns a dictionary of domain ID numbers and the name that corresponds. Since inactive
    domains do not have ID numbers, they are not included in the returned dict'''
    domain_names = {}
    
    domain_ids = conn.listDomainsID()
    if domain_ids == None:
        print('Failed to get a list of domain IDs', file=sys.stderr)

    if len(domain_ids) == 0:
        print('No active domains')
    else:
        for domain_id in domain_ids:
            domain = conn.lookupByID(domain_id)
            domain_names[domain_id] = domain.name()
        return domain_names


def domain_state(domain_name, conn):
    '''Takes in the name of a domain and a connection object; returns the state of the domain and the reason it is in that state'''
    domain = conn.lookupByName(domain_name)
    
    if domain == None:
       print('Failed to find the domain '+domain_name, file=sys.stderr)
       exit(1)

    state_code, reason_code = domain.state()

    domain_states = {
        0: 'VIR_DOMAIN_NOSTATE',
        1: 'VIR_DOMAIN_RUNNING',
        2: 'VIR_DOMAIN_BLOCKED',
        3: 'VIR_DOMAIN_PAUSED',
        4: 'VIR_DOMAIN_SHUTDOWN',
        5: 'VIR_DOMAIN_SHUTOFF',
        6: 'VIR_DOMAIN_CRASHED',
        7: 'VIR_DOMAIN_PMSUSPENDED',
    }

    domain_reasons = {
        'VIR_DOMAIN_NOSTATE': { 0: 'VIR_DOMAIN_NOSTATE_UNKNOWN' },
        'VIR_DOMAIN_RUNNING': { 0: 'VIR_DOMAIN_RUNNING_UNKNOWN', 
                                1: 'VIR_DOMAIN_RUNNING_BOOTED',
                                2: 'VIR_DOMAIN_RUNNING_MIGRATED',
                                3: 'VIR_DOMAIN_RUNNING_RESTORED',
                                4: 'VIR_DOMAIN_RUNNING_FROM_SNAPSHOT',
                                5: 'VIR_DOMAIN_RUNNING_UNPAUSED',
                                6: 'VIR_DOMAIN_RUNNING_MIGRATION_CANCELED',
                                7: 'VIR_DOMAIN_RUNNING_SAVE_CANCELED',
                                8: 'VIR_DOMAIN_RUNNING_WAKEUP',
                                9: 'VIR_DOMAIN_RUNNING_CRASHED',
                                10: 'VIR_DOMAIN_RUNNING_POSTCOPY', },
        'VIR_DOMAIN_BLOCKED': { 0: 'VIR_DOMAIN_BLOCKED_UNKNOWN' },
        'VIR_DOMAIN_PAUSED': { 0: 'VIR_DOMAIN_PAUSED_UNKNOWN',
                               1: 'VIR_DOMAIN_PAUSED_USER',
                               2: 'VIR_DOMAIN_PAUSED_MIGRATION',
                               3: 'VIR_DOMAIN_PAUSED_SAVE',
                               4: 'VIR_DOMAIN_PAUSED_DUMP',
                               5: 'VIR_DOMAIN_PAUSED_IOERROR',
                               6: 'VIR_DOMAIN_PAUSED_WATCHDOG',
                               7: 'VIR_DOMAIN_PAUSED_FROM_SNAPSHOT',
                               8: 'VIR_DOMAIN_PAUSED_SHUTTING_DOWN',
                               9: 'VIR_DOMAIN_PAUSED_SNAPSHOT',
                               10: 'VIR_DOMAIN_PAUSED_CRASHED',
                               11: 'VIR_DOMAIN_PAUSED_STARTING_UP',
                               12: 'VIR_DOMAIN_PAUSED_POSTCOPY',
                               13: 'VIR_DOMAIN_PAUSED_POSTCOPY_FAILED', },
        'VIR_DOMAIN_SHUTDOWN': { 0: 'VIR_DOMAIN_SHUTDOWN_UNKNOWN',
                                 1: 'VIR_DOMAIN_SHUTDOWN_USER', },
        'VIR_DOMAIN_SHUTOFF': { 0: 'VIR_DOMAIN_SHUTOFF_UNKNOWN', 
                                1: 'VIR_DOMAIN_SHUTOFF_SHUTDOWN',
                                2: 'VIR_DOMAIN_SHUTOFF_DESTROYED',
                                3: 'VIR_DOMAIN_SHUTOFF_CRASHED',
                                4: 'VIR_DOMAIN_SHUTOFF_MIGRATED',
                                5: 'VIR_DOMAIN_SHUTOFF_SAVED',
                                6: 'VIR_DOMAIN_SHUTOFF_FAILED',
                                7: 'VIR_DOMAIN_SHUTOFF_FROM_SNAPSHOT',
                                8: 'VIR_DOMAIN_SHUTOFF_DAEMON', },
        'VIR_DOMAIN_CRASHED': { 0: 'VIR_DOMAIN_CRASHED_UNKNOWN',
                                1: 'VIR_DOMAIN_CRASHED_PANICKED', },
        'VIR_DOMAIN_PMSUSPENDED': { 0: 'VIR_DOMAIN_PMSUSPENDED_DISK_UNKNOWN', } 
    }

    state = domain_states[state_code]
    reason = domain_reasons[state][reason_code]

    return state, reason

