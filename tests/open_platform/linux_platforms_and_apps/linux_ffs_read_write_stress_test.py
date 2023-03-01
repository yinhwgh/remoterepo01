import sys
import os
import unicorn
import shutil
import time
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart

from dstl.embedded_system.linux.configuration import dstl_embedded_linux_adb_configuration
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
from dstl.identification.check_identification_ati import dstl_check_ati1_response

dir = "LinuxFfsReadWriteStressTest"

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('external')
        
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
        os.mkdir(dir)
 

        

    def run(test):
    
        # query product version with ati
        test.expect(dstl_check_ati1_response(test.dut))
        
        test.ssh_server.send_and_receive(f"pwd")
        path_to_sdk = test.ssh_server.last_response.rstrip()+"/"
        
       
        
        test.ssh_server.send_and_receive(f"mkdir {dir}")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.upload(f"{sys.path[0]}/external_repos/linux_src/src/scripts/var/LinuxFfsReadWriteStressTest/build_stress_app.sh", f"./{dir}/build_stress_app.sh")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.send_and_receive(f"cd ./{dir} && chmod +x build_stress_app.sh")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.send_and_receive(f"cd ./{dir} && ./build_stress_app.sh ../linux_src")
        test.expect(test.ssh_server.last_retcode == 0)
        
        test.ssh_server.download(f"{path_to_sdk}/{dir}/stress", f"./{dir}/stress")
        test.expect(test.ssh_server.last_retcode == 0)
        
      
        test.dut.adb.push(f"./{dir}/stress", "/home/stress")
        test.expect(test.dut.adb.last_retcode == 0)
        
        test.dut.adb.send_and_receive(f"chmod +x /home/stress")
        test.expect(test.dut.adb.last_retcode == 0)
        
        test.dut.adb.send_and_verify(f"while true; do echo `date`; sleep 60; done & /home/stress -c 2 -i 1 -m 1 --vm-bytes 4M -t 300s", "successful run completed")
        test.expect(test.dut.adb.last_retcode == 0)
        
        test.dut.adb.send_and_verify(f"while true; do echo `date`; sleep 60; done & /home/stress -c 10 -i 10 -m 2 --vm-bytes 4M -t 600s", "successful run completed")
        test.expect(test.dut.adb.last_retcode == 0)
        
        test.dut.adb.send_and_receive(f"while true; do echo `date`; sleep 60; done & /home/stress -c 1 -i 1 -m 2 --vm-bytes 256M -t 600s", "successful run completed")
        test.expect(test.dut.adb.last_retcode != 0)
        
        test.dut.at1.wait_for(".*SYSSTART.*|.*SYSLOADING.*", timeout = 90)
        
        time.sleep(30)

        test.dut.adb.send_and_receive(f"while true; do echo `date`; sleep 60; done & /home/stress -c 120 -i 20 -m 2 --vm-bytes 4M -t 6h", "successful run completed")
        test.expect(test.dut.adb.last_retcode == 0)
      



    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')
        test.os.execute(f"rm -rf {dir}")
        test.dut.adb.send_and_receive(f"rm -rf /home/stress")
        test.ssh_server.send_and_receive(f"rm -rf {dir}")

if "__main__" == __name__:
    unicorn.main()
    