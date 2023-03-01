# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102418.001 arc_data_start_stop_loop.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilDataAuthTypeInParallel', build=True)
        
    def run(test):
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilDataAuthTypeInParallel",
            params = [
            "l=80",
            "ip1={}".format(''),
            "ip2={}".format(''),
            "apn={}".format(test.dut.sim.apn_v4 or 'internet'),
            "apn2={}".format(''),
            "user={}".format(''),
            "user2={}".format(''),
            "passwd={}".format(''),
            "passwd2={}".format('')
            ],
            expect='EXP')
        

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
