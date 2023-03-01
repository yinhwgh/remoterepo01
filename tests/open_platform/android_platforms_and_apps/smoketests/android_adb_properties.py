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
    
        test.log.step("Step 1: Getting IMEI")
        output = test.dut.adb.send_and_receive(f"service call iphonesubinfo 1 | toybox cut -d \"'\" -f2 | toybox grep -Eo '[0-9]' | toybox xargs | toybox sed 's/\ //g'")
        test.log.info(f"IMEI: {output}")
        test.expect(output.strip())
        test.log.step("Step 2: Getting ro.vendor.thales.version.arn")
        output = test.dut.adb.send_and_receive('getprop ro.vendor.thales.version.arn')
        test.log.info(f"ARN: {output}")
        test.expect(output.strip())
        test.log.step("Step 3: Getting ro.vendor.thales.version.svn")
        output = test.dut.adb.send_and_receive('getprop ro.vendor.thales.version.svn')
        test.log.info(f"SVN: {output}")
        test.expect(output.strip())
        test.log.step("Step 4: Getting ro.vendor.thales.version.revision")
        output = test.dut.adb.send_and_receive('getprop ro.vendor.thales.version.revision')
        test.log.info(f"REVISION: {output}")
        test.expect(output.strip())
        test.log.step("Step 5: Getting ro.vendor.thales.platform")
        output = test.dut.adb.send_and_receive('getprop ro.vendor.thales.platform')
        test.log.info(f"PLATFORM: {output}")
        test.expect(output.strip())
        test.log.step("Step 6: Getting ro.vendor.build.fingerprint")
        output = test.dut.adb.send_and_receive('getprop ro.vendor.build.fingerprint')
        test.log.info(f"FINGERPRINT: {output}")
        test.expect(output.strip())
        test.log.step("Step 7: Getting ro.bootimage.build.fingerprint")
        output = test.dut.adb.send_and_receive('getprop ro.bootimage.build.fingerprint')
        test.log.info(f"FINGERPRINT: {output}")
        test.expect(output.strip())
        test.log.step("Step 8: sending wrong property value")
        output = test.dut.adb.send_and_receive('getprop XXX')
        test.expect(not output.strip())
        test.log.step("Step 9: Getting complete property list")
        output = test.dut.adb.send_and_receive('getprop ')
        test.expect(output.strip())
        test.log.step("Step 10: reboot module via adb command")
        output = test.dut.adb.send_and_receive('getprop ro.vendor.thales.platform')
        test.expect(output.strip())
        output = test.dut.adb.send_and_receive('reboot')
        test.expect(test.dut.adb.last_retcode == -1)
        time.sleep(90)
        output = test.dut.adb.send_and_receive('pwd')
        test.expect(test.dut.adb.last_retcode == 0)
        
        
 
        
       
        



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
