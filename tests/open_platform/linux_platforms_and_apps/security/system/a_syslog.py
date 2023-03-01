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
        test.log.info(f"log clear")
        ret1 = test.dut.adb.send_and_receive("> /var/log/messages")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
        
#---------------------------------------------------------------------------------------    
        test.log.info(f"Check with root: write/read")
        ret1 = test.dut.adb.send_and_receive(f"logger echo {STR}")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
                
                
        ret1 = test.dut.adb.send_and_receive(f"grep -q {STR} /var/log/messages")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
                
 #---------------------------------------------------------------------------------------   
        test.log.info(f"Check with non-root: write/read")
        ret1 = test.dut.adb.send_and_receive(f"su nobody -c \"logger test_user_write\"")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
                
                
        ret1 = test.dut.adb.send_and_receive(f"su nobody -c \"grep -q test_user_write /var/log/messages\"")
        if( test.dut.adb.last_retcode == 0):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 0")
                test.expect(False)
                
 #---------------------------------------------------------------------------------------        


    def cleanup(test):
        pass