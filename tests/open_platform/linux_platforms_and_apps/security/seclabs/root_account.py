# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn

from core.basetest import BaseTest

dir = "temp_root_account_path"

USER_LIST_CHECK=['root']



class Test(BaseTest):

    def setup(test):
    
       
        pass

    def run(test):

#---------------------------------------------------------------------------------------        
        test.log.info(f"Check root accounts")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("cut -d: -f1 /etc/shadow")
        test.expect(test.dut.adb.last_retcode == 0)
        accounts_list = list(test.dut.adb.last_response.split("\n"))
        for i in accounts_list:
            if search(USER_LIST_CHECK, i.rstrip() ):
                print(f"User: {i}")
                test.dut.adb.send_and_receive("cat /etc/shadow | grep root: | grep -qw -e \"!\" -e \"!!\" -e \"*\"")
                test.expect(test.dut.adb.last_retcode == 0)
              
            
        
#---------------------------------------------------------------------------------------    


    def cleanup(test):
        

        pass
        
        
def search(list, line):
    for i in range(len(list)):
        if list[i] == line:
            return True
    return False