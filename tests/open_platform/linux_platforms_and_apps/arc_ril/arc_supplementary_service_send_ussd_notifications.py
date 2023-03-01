# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0104040.001 arc_supplementary_service_send_ussd_notifications.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilSupplementaryServiceFunctional')
        
    def run(test):

        test.sleep(5)

        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
            params="CS_GET {}".format(test.dut.sim.pin1),
            expect='')           
           
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
            params="USSD_SND * {}".format(test.dut.sim.pin1),
            expect='USSD NOSUPPORT')            
           
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
            params="USSD_SND *100# {}".format(test.dut.sim.pin1),
            expect='NOTIFICATION RECEIVED')   

        test.expect('USSD INTERACTIV' in response or 'USSD NORMAL' in response)


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
