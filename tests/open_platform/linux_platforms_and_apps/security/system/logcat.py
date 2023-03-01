# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn
from core.basetest import BaseTest



class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        STR="test_root_message"
#---------------------------------------------------------------------------------------        
        test.log.info(f"Check with root")
#---------------------------------------------------------------------------------------        
        test.log.info(f"logcat log clear, optional")
        ret1 = test.dut.adb.send_and_receive("logcat -c")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
    

        test.log.info(f"write as root user") 
        ret1 = test.dut.adb.send_and_receive(f"log {STR}")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
                
                
        test.log.info(f"read as root user") 
        ret1 = test.dut.adb.send_and_receive(f"logcat -T 1 -d | grep {STR}")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)      
#---------------------------------------------------------------------------------------    
        test.log.info(f"Check with non-root")
#--------------------------------------------------------------------------------------- 
        test.log.info(f"logcat log clear, optional")
        ret1 = test.dut.adb.send_and_receive("logcat -c")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
    
    
        test.log.info(f"write as non-root user") 
        test.log.info(f"use audio user as an example of user in logd group")

        ret1 = test.dut.adb.send_and_receive(f"su --preserve-environment audio -c \"log test_user_write\"")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
                
                
        test.log.info(f"read as non-root user") 
        ret1 = test.dut.adb.send_and_receive(f"su --preserve-environment audio -c \"logcat -T 1 -d | grep test_user_write\"")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False) 
#---------------------------------------------------------------------------------------                
    
    def cleanup(test):
        pass