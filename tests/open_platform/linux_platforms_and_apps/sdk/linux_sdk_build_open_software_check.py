import sys
import unicorn
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

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('external')

        

    def run(test):
    
        # query product version with ati
        test.expect(dstl_check_ati1_response(test.dut))
        
        test.ssh_server.send_and_receive(f'python3 /srv/appbuilder/sdk_setup.py --sw {test.dut.software}')
        test.ssh_server.send_and_verify("ls -la ./sdk", "..")
        
        test.ssh_server.send_and_receive(f"pwd")
        path_to_sdk = test.ssh_server.last_response.rstrip()+"/"
        
        
        test.ssh_server.upload(f"{sys.path[0]}/external_repos/linux_src/src/scripts/sdk/LinuxSDKBuildSoftwareCheck/LinuxSDKBuildSoftwareCheck.sh", f"./LinuxSDKBuildSoftwareCheck.sh")
        
        test.ssh_server.send_and_receive(f"chmod +x {path_to_sdk}LinuxSDKBuildSoftwareCheck.sh")
        test.expect(test.ssh_server.last_retcode == 0)
        
        ret1 = test.ssh_server.send_and_verify(f"while true; do echo `date`; sleep 20; done & source /usr/local/oecore-x86_64/environment-setup-cortexa8hf-vfp-neon-oe-linux-gnueabi && {path_to_sdk}LinuxSDKBuildSoftwareCheck.sh",f"COM:App finish work")
        test.expect(ret1)
        test.expect(test.ssh_server.last_retcode == 0)
        
        

        



    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')
        test.ssh_server.send_and_receive(f"if [ -d /tmp/st ]; then rm -rf /tmp/st; fi")
        test.ssh_server.send_and_receive(f"if [ -d /tmp/bins ]; then rm -rf /tmp/bins; fi")
        test.ssh_server.send_and_receive(f"if [ -d /tmp/*/bins ]; then rm -rf /tmp/*/bins; fi")

if "__main__" == __name__:
    unicorn.main()