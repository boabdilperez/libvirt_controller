import libvirt
import sys
from xml.dom import minidom

CONNSTRING = 'qemu:///system'


def _get_ro_conn():
    '''Returns a read-only connection to the local qemu hypervisor'''
    conn = libvirt.openReadOnly(CONNSTRING)
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)
    else:
        return conn


def _get_conn():
    '''Returns a read/write connection to the local qemu hypervisor'''
    conn = libvirt.open(CONNSTRING)
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)
    else:
        return conn


def list_all_domains():
    '''Returns a list of all domains on a hypervisor, active or not'''
    conn = _get_ro_conn()
    domain_names = conn.listDefinedDomains()

    domain_ids = conn.listDomainsID()
    if domain_ids == None:
        print('Failed to get a list of domain IDs', file=sys.stderr)
        conn.close()
        exit(1)

    if len(domain_ids) != 0:
        for domain_id in domain_ids:
            domain = conn.lookupByID(domain_id)
            domain_names.append(domain.name())
    elif len(domain_ids) == 0:
        conn.close()
        return "No domains"

    conn.close()
    return domain_names


def list_active_domains():
    '''Returns a list of active domains on this hypervisor'''
    conn = _get_ro_conn()
    domain_names = {}

    domain_ids = conn.listDomainsID()
    if domain_ids == None:
        print('Failed to get a list of domain IDs', file=sys.stderr)
        conn.close()
        exit(1)

    if len(domain_ids) == 0:
        conn.close()
        return 'No active domains'
    else:
        for domain_id in domain_ids:
            domain = conn.lookupByID(domain_id)
            domain_names[domain_id] = domain.name()
        conn.close()
        return domain_names


def domain_state(domain_name):
    '''Takes in the name of a domain; returns the state of the domain and the reason it is in that state'''
    conn = _get_ro_conn()
    domain = conn.lookupByName(domain_name)

    if domain == None:
        print('Failed to find the domain '+domain_name, file=sys.stderr)
        conn.close()
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
        'VIR_DOMAIN_NOSTATE': {0: 'VIR_DOMAIN_NOSTATE_UNKNOWN'},
        'VIR_DOMAIN_RUNNING': {0: 'VIR_DOMAIN_RUNNING_UNKNOWN',
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
        'VIR_DOMAIN_BLOCKED': {0: 'VIR_DOMAIN_BLOCKED_UNKNOWN'},
        'VIR_DOMAIN_PAUSED': {0: 'VIR_DOMAIN_PAUSED_UNKNOWN',
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
        'VIR_DOMAIN_SHUTDOWN': {0: 'VIR_DOMAIN_SHUTDOWN_UNKNOWN',
                                1: 'VIR_DOMAIN_SHUTDOWN_USER', },
        'VIR_DOMAIN_SHUTOFF': {0: 'VIR_DOMAIN_SHUTOFF_UNKNOWN',
                               1: 'VIR_DOMAIN_SHUTOFF_SHUTDOWN',
                               2: 'VIR_DOMAIN_SHUTOFF_DESTROYED',
                               3: 'VIR_DOMAIN_SHUTOFF_CRASHED',
                               4: 'VIR_DOMAIN_SHUTOFF_MIGRATED',
                               5: 'VIR_DOMAIN_SHUTOFF_SAVED',
                               6: 'VIR_DOMAIN_SHUTOFF_FAILED',
                               7: 'VIR_DOMAIN_SHUTOFF_FROM_SNAPSHOT',
                               8: 'VIR_DOMAIN_SHUTOFF_DAEMON', },
        'VIR_DOMAIN_CRASHED': {0: 'VIR_DOMAIN_CRASHED_UNKNOWN',
                               1: 'VIR_DOMAIN_CRASHED_PANICKED', },
        'VIR_DOMAIN_PMSUSPENDED': {0: 'VIR_DOMAIN_PMSUSPENDED_DISK_UNKNOWN', }
    }

    state = domain_states[state_code]
    reason = domain_reasons[state][reason_code]

    conn.close()
    return state, reason
