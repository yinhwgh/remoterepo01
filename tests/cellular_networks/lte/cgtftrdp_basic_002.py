#responsible: yuan.gao@thalesgroup.com
#location: Dalian
#TC0091662.002

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain import config_pdp_context


class Test(BaseTest):
    """
    TC0091662.002 - CgtftrdpBasic_Dahlia
    check the basic functionality of the AT command +CGTFTRDP

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.apn1 = test.dut.sim.apn_v4
        test.dut.dstl_register_to_lte()

    def run(test):
        maxcid = test.dut.dstl_get_supported_max_cid()
        test.log.info('1.Define Pdp context')

        for i in range(4, maxcid+1):
            test.expect(test.dut.at1.send_and_verify(f"at+cgdcont={i},\"IP\",\"{test.apn1}\"", "OK"))

        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp'))

        test.log.info('2.Activate PDP context')
        test.expect(test.dut.at1.send_and_verify('at+cgact=1,2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact=1,3', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact?', '.*\+CGACT: 2,1.*|.*\+CGACT: 3,1.*'))

        test.log.info('3.Check command of cgtftrdp')
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=?', '.*\+CGTFTRDP: \(.*\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=3', 'OK'))

        test.log.info('4.Check invalid parameter')
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=17', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=a', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=#', 'ERROR'))

        test.log.info('5.Deactivate PDP context')
        test.expect(test.dut.at1.send_and_verify('at+cgact=0,2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact=0,3', 'OK'))

        test.log.info('6.Check command of cgtftrdp')
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=?', '.*\+CGTFTRDP: \(.*\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=3', 'OK'))

        test.log.info('delete defined PDP contexts')
        for i in range(4, maxcid + 1):
            test.dut.dstl_delete_pdp_context(i)



    def cleanup(test):
        pass





if (__name__ == "__main__"):
    unicorn.main()
