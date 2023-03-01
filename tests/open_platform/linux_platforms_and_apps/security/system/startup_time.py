# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn

from core.basetest import BaseTest

dir = "temp_startup_time_path"

max_boot_time = 40.00  #secound

max_kernel_time = 12.00 #secound

max_user_space_time = 30.00 #secound

tmpf = 0.0 # temp variable
tmp = "" #temp variable for boot time


#Trigger list to check
TRIGGERS_TO_CHECK=[
'3.5 Booting Linux on physical CPU 0x0',
'5.0 Freeing unused kernel memory:',
'11.0 pil-q6v5-mss 4080000.qcom,mss: modem: loading from 0x88000000 to 0x8ee00000',
'12.5 cust-init: start',
'20.0 pil-q6v5-mss 4080000.qcom,mss: modem: Brought out of reset'
]



class Test(BaseTest):

    def setup(test):
    
       
        pass

    def run(test):
        STR="test_root_message"
#---------------------------------------------------------------------------------------        
        test.log.info(f"Push systemd-analyze to /tmp/")
#---------------------------------------------------------------------------------------        
        ret1 = test.dut.adb.push(f"./tests/open_platform/linux_platforms_and_apps/security/packages/systemd-analyze", "/tmp/")
        test.expect(ret1)
#---------------------------------------------------------------------------------------    
        test.log.info(f"Check  systemd-analyze in /tmp")
#--------------------------------------------------------------------------------------- 
        ret2 = test.dut.adb.send_and_verify(f"ls -al /tmp/", ".*systemd-analyze.*")
        test.expect(ret2)
#---------------------------------------------------------------------------------------                
        test.log.info(f"Check an overview of the system boot-up time (kernel&userspace&sum)")
#--------------------------------------------------------------------------------------- 
        ret3 = test.dut.adb.send_and_receive(f"/tmp/systemd-analyze")
        test.expect(test.dut.adb.last_retcode == 0)
#--------------------------------------------------------------------------------------- 
        
        ret3 = test.dut.adb.send_and_receive("/tmp/systemd-analyze |  awk '{print $4; exit}' | sed 's/.$//'")
        test.expect(test.dut.adb.last_retcode == 0)
        tmpf= float(tmp.join(test.dut.adb.last_response.split("\n")))
        test.log.info(f"Comparison: kernel boot time {tmpf} < {max_kernel_time} max kernel boot time")
        test.expect(tmpf < max_kernel_time)
#---------------------------------------------------------------------------------------
        
        ret3 = test.dut.adb.send_and_receive("/tmp/systemd-analyze |  awk '{print $10; exit}' | sed 's/.$//'")
        test.expect(test.dut.adb.last_retcode == 0)
        tmpf= float(tmp.join(test.dut.adb.last_response.split("\n")))
        test.log.info(f"Comparison: user space boot time {tmpf} < {max_user_space_time} max userspace boot time")
       
        test.expect(tmpf < max_user_space_time)
#---------------------------------------------------------------------------------------
        
        ret3 = test.dut.adb.send_and_receive("/tmp/systemd-analyze |  awk 'END{print $4}' | sed 's/.$//'")
        test.expect(test.dut.adb.last_retcode == 0)
        tmpf= float(tmp.join(test.dut.adb.last_response.split("\n")))
        test.log.info(f"Comparison: multi-user.target reached : {tmpf} < {max_boot_time} max userspace boot time")
       
        test.expect(tmpf < max_boot_time)
#---------------------------------------------------------------------------------------
        
    def cleanup(test):
        pass
        
        
 
