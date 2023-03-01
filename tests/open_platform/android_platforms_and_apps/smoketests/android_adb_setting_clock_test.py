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
    
        
        
        
        
        
        test.log.step("Step 1: Set date")
        output = test.dut.adb.send_and_verify('su 0 date 073013182021.25 ; su 0 am broadcast -a android.intent.action.TIME_SET',".*Fri.*Jul.*30.*13:18:25.*CEST.*2021.*")
        test.expect(output)
        test.log.step("Step 2: Reboot and set date")
        output = test.dut.adb.send_and_receive('reboot')
        test.expect(test.dut.adb.last_retcode == -1)
        time.sleep(90)
        
        
        test.log.step("Wait for SIM LOADED")
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
        
        
        
        output = test.dut.adb.send_and_verify('su 0 date 073013182021.25 ; su 0 am broadcast -a android.intent.action.TIME_SET',".*Fri.*Jul.*30.*13:18:25.*CEST.*2021.*")
        test.expect(output)
        test.log.step("Step 3: Negative test : Set invalid day")
        output = test.dut.adb.send_and_verify('su 0 date 074213182021.25 ; su 0 am broadcast -a android.intent.action.TIME_SET',".*bad.*date.*")
        test.expect(output)
        test.log.step("Step 4: Negative test : Set invalid month")
        output = test.dut.adb.send_and_verify('su 0 date 133013182021.25 ; su 0 am broadcast -a android.intent.action.TIME_SET',".*bad.*date.*")
        test.expect(output)
        test.log.step("Step 5: Negative test : Set invalid year")
        output = test.dut.adb.send_and_verify('su 0 date 07301318202a.25 ; su 0 am broadcast -a android.intent.action.TIME_SET',".*bad.*date.*")
        test.expect(output)
        test.log.step("Step 6: Negative test : Set invalid hour")
        output = test.dut.adb.send_and_verify('su 0 date 073028182021.25 ; su 0 am broadcast -a android.intent.action.TIME_SET',".*bad.*date.*")
        test.expect(output)
        test.log.step("Step 7: Negative test : Set invalid minute")
        output = test.dut.adb.send_and_verify('su 0 date 073013922021.25 ; su 0 am broadcast -a android.intent.action.TIME_SET',".*bad.*date.*")
        test.expect(output)
        test.log.step("Step 8: Negative test : Set invalid second")
        output = test.dut.adb.send_and_verify('su 0 date 073013182021.91 ; su 0 am broadcast -a android.intent.action.TIME_SET',".*bad.*date.*")
        test.expect(output)
        
        
        
        
        
        #print(test.dut.platform)
        #print(test.dut.product)
        #print(test.dut.project)
        #print(test.dut.step)
        #print(test.dut.variant)
        #print(test.dut.software)
        



    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
