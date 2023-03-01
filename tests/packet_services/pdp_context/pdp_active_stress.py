#responsible: dan.liu@thalesgroup.com
#location: Dalian
#TC0095840.001


import unicorn

from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.packet_domain import config_pdp_context
from dstl.configuration import set_autoattach
from dstl.network_service import register_to_network
from dstl.internet_service.connection_setup_service import connection_setup_service
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object


class pdpactivestress(BaseTest):
    '''
       TC0095840.001 - PDPActiveStress
       PDP context for each serial port (or virtual serial port) can be active by Qos setting
    '''

    def setup(test):

        test.dut.dstl_detect()
        test.log.info("init the test ")
        test.dut.dstl_enable_ps_autoattach()
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()

    def run(test):

        test.log.info("1. Active GPRS attach")
        run_time = 1

        while run_time < 100:

            pdpactivestress_obj = dstl_get_connection_setup_object(test.dut, ip_public=True)

            pdpactivestress_obj.dstl_attach_to_packet_domain()

            test.log.info("2. Define a pdp context cid=2")

            pdpactivestress_obj.cgdcont_parameters['cid'] = "2"

            pdpactivestress_obj.cgdcont_parameters['pdp_type'] = "ipv4v6"

            pdpactivestress_obj.cgdcont_parameters['apn'] = "internet"

            pdpactivestress_obj.dstl_define_pdp_context()

            test.log.info("3.  Set default value for Qos Profile minimum acceptable")

            test.expect(test.dut.at1.send_and_verify("at+cgeqos=2,0,0,0,0,0", ".*OK.*"))

            test.log.info("4.  Set any value for Qos profile requestede")

            test.expect(test.dut.at1.send_and_verify("AT+CGEQOS=2,1,128,128,384,384", ".*OK.*"))

            test.log.info("5.   Active the PDP contexte")

            pdpactivestress_obj.dstl_activate_pdp_context()

            test.log.info("6.   check actual address and activation state")

            pdpactivestress_obj.dstl_get_pdp_address(cid=2)

            run_time = run_time + 1

    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
