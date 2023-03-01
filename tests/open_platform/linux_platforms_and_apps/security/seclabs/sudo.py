# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn

from core.basetest import BaseTest

dir = "temp_su_path"


# List of allowed sudo rules
WHITELIST=[ "atcextd", "bearerctl", "pdcd", "rebootd", "syshalt", "gomadm", "ril"]



class Test(BaseTest):

    def setup(test):
    
       
        pass

    def run(test):

#---------------------------------------------------------------------------------------        
        test.log.info(f"Check sudo application")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive(f"which sudo")
        if( test.dut.adb.last_retcode == 0):
            test.expect(True)
        else:
            test.log.error("last_retcode unequal 0")
            test.expect(False)
#---------------------------------------------------------------------------------------    

        test.dut.adb.send_and_receive("ls -1 --color=never /etc/sudoers.d")
        test.expect(test.dut.adb.last_retcode == 0)
        rules_list = list(test.dut.adb.last_response.split("\n"))
        
        

    def cleanup(test):
        

        pass