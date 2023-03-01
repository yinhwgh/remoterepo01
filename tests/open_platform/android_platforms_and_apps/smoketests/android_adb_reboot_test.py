# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096511.001 arc_daemon.py

import unicorn
import time
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot


adb_serial = '0123456789ABCDEF'
adb_remote = 'd54941ee'
phone_number_dut = '+48668168409'
phone_number_remote = '+48697660585'


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        
        test.log.step("Check adb in basic system: ")
        ret = test.os.execute_and_verify("adb version", "Android Debug Bridge version 1.0.4")
        test.expect(ret)
        test.log.step("Check adb Tiger devices: ")
        ret = test.os.execute_and_verify("adb devices", "0123456789ABCDEF")
        test.expect(ret)
        
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_serial} shell getprop | grep 'gsm.sim.state'","LOADED.*ABSENT")
            time.sleep(5)
            if output == False:
                test.os.execute(f"adb -s {adb_serial} shell input text 9999") 
                test.os.execute(f"adb -s {adb_serial} shell input keyevent 66")
                time.sleep(5)
                output = test.os.execute_and_verify(f"adb -s {adb_serial} shell getprop | grep 'gsm.sim.state'","LOADED.*ABSENT")
        test.expect(output)
        
        test.log.step("Check adb function")
        test.dut.adb.send_and_receive('su 0 whoami')
        test.expect('root' in test.dut.adb.last_response)
        


    def run(test):
    
        
        test.log.info(f"Step 1: Restart module in a loop of 2 without Pin entered and network registration")
    
        for x in range(2):
            test.log.info(f"++++++++++++++++++++++++ restart loop {x+1} ++++++++++++++++++++++++")
            test.log.step("Step: reset module")
            output = test.dut.adb.send_and_receive('reboot')
            test.expect(test.dut.adb.last_retcode == -1)
            test.log.step("Step: wait for restart 90s")
            time.sleep(90)
            
            test.log.step("Step: check adb interface")
            output = test.dut.adb.send_and_verify('pwd','/')
            test.expect(output)
            
            test.log.step("Step: check modem version")
            output = test.dut.adb.send_and_receive('getprop ro.vendor.md_apps.load_verno')
            test.expect(output.strip())
            
            test.log.step("Step: check SIM PIN")
            output = test.os.execute_and_verify(f"adb -s {adb_serial} shell getprop | grep 'gsm.sim.state'","PIN_REQUIRED.*")
            test.expect(output)
            
            
           
        
        test.log.info(f"Step 2: Restart module in a loop of 2 with Pin and network registration")
        
        for x in range(2):
            test.log.info(f"++++++++++++++++++++++++ restart loop {x+1} ++++++++++++++++++++++++")
            test.log.step("Step: reset module")
            output = test.dut.adb.send_and_receive('reboot')
            test.expect(test.dut.adb.last_retcode == -1)
            test.log.step("Step: wait for restart 90s")
            time.sleep(90)
            
            test.log.step("Step: check adb interface")
            output = test.dut.adb.send_and_verify('pwd','/')
            test.expect(output)
            
            test.log.step("Step: check modem version")
            output = test.dut.adb.send_and_receive('getprop ro.vendor.md_apps.load_verno')
            test.expect(output.strip())
            
            test.log.step("Step: unlock SIM CARD")
            output = False
            output = False
            while output == False:
                output = test.os.execute_and_verify(f"adb -s {adb_serial} shell getprop | grep 'gsm.sim.state'","LOADED.*ABSENT")
                time.sleep(5)
                if output == False:
                    test.os.execute(f"adb -s {adb_serial} shell input text 9999") 
                    test.os.execute(f"adb -s {adb_serial} shell input keyevent 66")
                    time.sleep(5)
                    output = test.os.execute_and_verify(f"adb -s {adb_serial} shell getprop | grep 'gsm.sim.state'","LOADED.*ABSENT")
            test.expect(output)
                
            time.sleep(5)
            
            test.log.step("Step: check network registration")
            output = False
            n = 0
            while output == False and n < 30:
                output = test.dut.adb.send_and_receive('getprop gsm.operator.numeric')
                test.expect(output.strip())
                output = output.strip()
                n=n+1
                time.sleep(2)
           
        time.sleep(5)
 
       
       
        



    def cleanup(test):
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_serial} shell getprop | grep 'gsm.sim.state'","LOADED.*ABSENT")
            time.sleep(5)
            if output == False:
                test.os.execute(f"adb -s {adb_serial} shell input text 9999") 
                test.os.execute(f"adb -s {adb_serial} shell input keyevent 66")
                time.sleep(5)
                output = test.os.execute_and_verify(f"adb -s {adb_serial} shell getprop | grep 'gsm.sim.state'","LOADED.*ABSENT")
        test.expect(output)


if "__main__" == __name__:
    unicorn.main()