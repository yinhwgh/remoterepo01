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
        
        time.sleep(5)
        test.log.step("Check network registration")
        output = False
        n = 0
        while output == False and n < 30:
            output = test.dut.adb.send_and_receive('getprop gsm.operator.numeric')
            test.expect(output.strip())
            output = output.strip()
            n=n+1
            time.sleep(2)
        
        test.log.step("Check adb function")
        test.dut.adb.send_and_receive('su 0 whoami')
        test.expect('root' in test.dut.adb.last_response)
        
        
        
        


    def run(test):
    
        test.log.step("Check adb in basic system: ")
        ret = test.os.execute_and_verify("adb version", "Android Debug Bridge version 1.0.4")
        test.expect(ret)
        test.log.step("Check adb Tiger devices: ")
        ret = test.os.execute_and_verify("adb devices", f"{adb_serial}.*{adb_remote}")
        test.expect(ret)
        
        test.log.step("Check adb basic shell cmd:")
        test.dut.adb.send_and_receive('su 0 whoami')
        test.expect('root' in test.dut.adb.last_response)
        
        test.log.step("Check screen resolution:")
        test.os.execute(f"adb -s {adb_serial} shell wm size")
        test.expect('720x1280' in test.os.last_response)
        
        test.log.step("Check adb basic shell cmd")
        test.os.execute(f"adb -s {adb_serial} shell wm density")
        test.expect('320' in test.os.last_response)
        
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_serial} shell dumpsys telephony.registry | grep mCallState | awk '{{print $1; exit}}'",".*0.*")
            time.sleep(5)
        test.expect(output)
        
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_remote} shell dumpsys telephony.registry | grep mCallState",".*0.*")
            time.sleep(5)
        test.expect(output)
        
        
        test.log.step("Call to dut from remote ")
        test.os.execute(f"adb -s {adb_remote} shell am start -a android.intent.action.CALL -d tel:{phone_number_dut} ")
        test.expect('act=android.intent.action.CALL' in test.os.last_response)
        time.sleep(5)
        
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_serial} shell dumpsys telephony.registry | grep  mCallState | awk '{{print $1; exit}}'",".*1.*")
            time.sleep(2)
        test.expect(output)
        
        test.os.execute(f"adb -s {adb_serial} shell input keyevent 5") 
        test.expect(test.os.last_retcode == 0)
        time.sleep(5)
        
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_serial} shell dumpsys telephony.registry | grep  mCallState | awk '{{print $1; exit}}'",".*2.*")
            time.sleep(2)
        test.expect(output)
        
        time.sleep(2)
        test.os.execute(f"adb -s {adb_serial} shell input keyevent 6") 
        test.expect(test.os.last_retcode == 0)
        time.sleep(2)
        
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_serial} shell dumpsys telephony.registry | grep mCallState  | awk '{{print $1; exit}}'",".*0.*")
            time.sleep(5)
        test.expect(output)
        
        
        test.log.step("Call from dut to remote ")
        
        test.os.execute(f"adb -s {adb_serial} shell am start -a android.intent.action.CALL -d tel:{phone_number_remote} ")
        test.expect('act=android.intent.action.CALL' in test.os.last_response)
        
        time.sleep(5)
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_remote} shell dumpsys telephony.registry | grep  mCallState ",".*1.*")
            time.sleep(2)
        test.expect(output)
        
        
        test.os.execute(f"adb -s {adb_remote} shell input keyevent 5") 
        test.expect(test.os.last_retcode == 0)
        time.sleep(5)
        
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_remote} shell dumpsys telephony.registry | grep  mCallState ",".*2.*")
            time.sleep(2)
        test.expect(output)
        
        time.sleep(2)
        test.os.execute(f"adb -s {adb_remote} shell input keyevent 6") 
        test.expect(test.os.last_retcode == 0)
        time.sleep(2)
        
        output = False
        while output == False:
            output = test.os.execute_and_verify(f"adb -s {adb_remote} shell dumpsys telephony.registry | grep mCallState ",".*0.*")
            time.sleep(5)
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
