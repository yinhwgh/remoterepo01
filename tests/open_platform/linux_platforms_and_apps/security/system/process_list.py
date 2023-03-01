# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn
from core.basetest import BaseTest



class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
    
        PROCESS_LIST_TO_CHECK=[
                '/usr/bin/ipacm_perf',
                '/usr/bin/ipacm',
                '/usr/bin/ipacmdiag',
                'QCMAP_ConnectionManager /data/mobileap_cfg.xml d',
                '/usr/bin/qti em usb',
                '/usr/bin/qseecomd',
                '/usr/bin/qseecomd',
                '/sbin/logd',
                '/usr/bin/time_daemon',
                '/usr/bin/thermal-engine',
                '/usr/bin/netmgrd',
                '/usr/bin/qmi_shutdown_modem',
                'seclauncher --user bearerctl --monitor --pidfile /var/run/monitored/bearerctld --capab CAP_NET_BIND_SERVICE CAP_NET_BROADCAST CAP_NET_ADMIN CAP_NET_RAW -a /usr/bin/bearerctld -f -i 01234567',
                '/usr/bin/bearerctld -f -i 01234567',
                'seclauncher --user audio --monitor --pidfile /var/run/monitored/audd.pid --stack 256 --logcat -a /usr/bin/audd',
                '/usr/bin/audd',
                '/usr/bin/adbd',
                '/usr/bin/dbus-daemon --system',
                '/sbin/reboot-daemon',
                'atcextd',
                '/usr/bin/diagrebootapp',
                'seclauncher --user ttysrvctl --monitor --pidfile /var/run/monitored/ttysrvctl.pid --stack 256 --logcat -a /usr/bin/ttysrvctl -m -g 7 -x /etc/ttysrvctl/ttysrvctl.xml --log-error kernel --log-warn kernel',
                '/usr/bin/ttysrvctl -m -g 7 -x /etc/ttysrvctl/ttysrvctl.xml --log-error kernel --log-warn kernel',
                '/usr/bin/ttyqmibridged -d /dev/ttyMDM_MPSS -i /RDM_MUX_DEV/0 -m 2',
                'seclauncher --user bearerctl --monitor --pidfile /var/run/monitored/bearerctld --capab CAP_NET_BIND_SERVICE CAP_NET_BROADCAST CAP_NET_ADMIN CAP_NET_RAW -a /usr/bin/bearerctld -f -i 01234567',
                '/usr/bin/ttyqmibridged -d /dev/ttyAPP_MPSS -i /RDM_MUX_DEV/1 -m 2',
                'seclauncher --user ril --monitor --pidfile /var/run/monitored/gto-rild.pid --stack 256 --logcat -a /usr/bin/gto-rild',
                '/usr/bin/gto-rild',
                '/usr/bin/pdc_daemon'


        ]

        
        test.log.info("Test that each critical process is in device process list")
        
        test.dut.adb.send_and_receive("ps  |  awk '{print $5}'")
        test.expect(test.dut.adb.last_retcode == 0)
     

        
        mode_list_ps = list(test.dut.adb.last_response.split("\n"))
        
        
        for i in mode_list_ps:
            print(f"{i}")
            test.expect( search(PROCESS_LIST_TO_CHECK, i.rstrip() ) )
        


    def cleanup(test):
        pass
        
        
        

def search(list, line):
    for i in range(len(list)):
        if list[i] == line:
            return True
    return False
