# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn
from core.basetest import BaseTest



class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        STR="test_dmesg"
        DBUS_APP_with_version=[
            'dbus-cleanup-sockets',
            'dbus-daemon',
            'dbus-launch', 
            'dbus-run-session', 
            'dbus-uuidgen'
        ]
        
        
        test.log.info(f"Check dbus library existence")
        ret1 = test.dut.adb.send_and_verify(f"find /usr/li* -name \"*dbus*\"", ".*libdbus-1.so.3.*")
        test.expect(ret1)
        
        
        test.log.info(f"Check if dbus services is running in systemd")
        ret1 = test.dut.adb.send_and_verify("systemctl | grep dbus", ".*dbus.service.*loaded.*active.*running.*")
        test.expect(ret1) 
        
        test.log.info(f"Check if dbus services is running in systemd")
        ret1 = test.dut.adb.send_and_verify("systemctl | grep dbus", ".*dbus.socket.*loaded.*active.*running.*")
        test.expect(ret1)
        
        test.log.info(f"Check if dbus daemon is running:  dbus.service")
        ret1 = test.dut.adb.send_and_verify("systemctl status dbus.service", ".*active.*(running).*")
        test.expect(ret1)  
        
        
        
        
        for i in DBUS_APP_with_version:
            print(f"{i}")
            test.log.info(f"Check dbus application: {i}")
            ret1 = test.dut.adb.send_and_receive(f"{i} --version")
            if( test.dut.adb.last_retcode == 0):
                test.expect(True)
            else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
                
        test.log.info(f"Check dbus application: dbus-monitor")
        ret1 = test.dut.adb.send_and_receive(f"dbus-monitor --version")
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)
                
        test.log.info(f"Check dbus application: dbus-send")
        ret1 = test.dut.adb.send_and_receive(f"dbus-send --version")
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)

        test.log.info(f"Check dbus application: dbus-update-activation-environment")
        ret1 = test.dut.adb.send_and_receive(f"dbus-update-activation-environment --version")
        if( test.dut.adb.last_retcode == 64):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 64")
                test.expect(False)
                
                
              

        test.log.info(f"Check if dbus works (dbus-send is used for it)")
        ret1 = test.dut.adb.send_and_verify("dbus-send --system --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames", ".*sender=org.freedesktop.DBus.*")
        test.expect(ret1)
        
        


    def cleanup(test):
        pass