#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091662.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain import config_pdp_context
from dstl.call import setup_voice_call


class Test(BaseTest):
    """
    TC0091662.001 - CgtftrdpBasic
    check the basic functionality of the AT command +CGTFTRDP

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_detect()
        test.sleep(3)
        test.apn1 = test.dut.sim.apn_v4
        test.dut.dstl_register_to_lte()
        test.r1.dstl_register_to_network()

    def run(test):
        maxcid = test.dut.dstl_get_supported_max_cid()
        int_r1_phone_num =test.r1.sim.int_voice_nr
        test.log.info('1.define all possible non-secondary and secondary PDP contexts')

        for i in range(4, maxcid+1):
            test.expect(test.dut.at1.send_and_verify(f"at+cgdcont={i},\"IP\",\"{test.apn1}\"", "OK"))

        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp'))

        test.expect(test.dut.at1.send_and_verify('at+cgact=1,5','OK'))

        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp=?', '.*\+CGTFTRDP: \(.*\).*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+cgact=1,2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact=1,3', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact?','.*\+CGACT: 2,1.*|.*\+CGACT: 3,1.*'))

        #with 4G sim card ,test by VOLTE
        test.expect(test.dut.at1.send_and_verify(f'atd{int_r1_phone_num};','OK'))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.dut.at1.send_and_verify('at+cgtftrdp','.*\+CGTFTRDP: \d+,\d+,\d+,".*",\d+,".*",".*",.*'))
        test.dut.dstl_release_call()
        test.expect(test.dut.at1.send_and_verify('at+cgact=0,5', 'OK'))
        test.log.info('delete defined PDP contexts')
        for i in range(4, maxcid + 1):
            test.dut.dstl_delete_pdp_context(i)


    def cleanup(test):
        pass





if (__name__ == "__main__"):
    unicorn.main()
