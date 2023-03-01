#responsible: tomasz.witka@globallogic.com
#location: Wroclaw
#TC0000000.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.performance import dstl_embedded_linux_check_cpu_usage
from dstl.embedded_system.linux.performance import dstl_embedded_linux_check_memory_usage
from dstl.embedded_system.linux.performance import dstl_embedded_linux_check_ril_status

"""
To collect KPI:
https://confluence.gemalto.com/display/GMVTIB/linux_idle_cpu+KPI+definition
https://confluence.gemalto.com/display/GMVTIB/linux_idle_memory+KPI+definition
https://confluence.gemalto.com/display/GMVTIB/linux_ril_status+KPI+definition

"""

class Test(BaseTest):
    
    def setup(test):
        test.require_plugin('adb')
        test.dut.dstl_detect()

    def run(test):
        test.expect(test.dut.dstl_embedded_linux_check_cpu_usage())
        test.expect(test.dut.dstl_embedded_linux_check_memory_usage())
        test.expect(test.dut.dstl_embedded_linux_check_ril_status())
        
    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()