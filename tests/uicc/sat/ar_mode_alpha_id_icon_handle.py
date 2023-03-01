#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0104451.001-ARmodeAlphaIDIconHandle

'''
Test with McTest4 board
'''

import unicorn
import re

from core.basetest import BaseTest

from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.usat import sim_instance

class ARmodeAlphaIDIconHandle(BaseTest):

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate DUT and restore to default configurations")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))


        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Register module to network")
        test.log.info("*******************************************************************")
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()

        test.log.info("*******************************************************************")
        test.log.info("SetUp_3: Switch on SAT/URC")
        test.log.info("*******************************************************************")
        test.dut.dstl_switch_on_sat_urc()

    def run(test):
        #1. PAC and TR of display text with icon
        pac_with_icon = '"D01A8103012180820281028D0B0442617369632049636F6E9E020001"'
        tr_with_icon ='"[08]103012180[08]2028281[08]30104"'


        #2. PAC and TR of Send short message with alpha ID, to be updated below PAC to a dynamic parameter.
        # For  the simmin sim card use below pac
        #pac_with_alphaID = '"D02F810301130082028183050D53686F7274204D65737361676506069153840910008B0D01010A91538455145841F20120"'

        # For the Beijing Erission test network sim card, use below pac
        #pac_with_alphaID = '"D0{2F}810301130082028183050D53686F7274204D65737361676506{06}91{5384091000}8B0D0101{0A}91{5384551458}41F20120"'
        pac_with_alphaID = '"D02F810301130082028183050D53686F7274204D65737361676506069194710803808B0D01010A91311966302741F20120"'
        tr_with_alphaID = '"[08]103011300[08]2028281[08]30100"'

        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Send a PAC of display text with icon, check the Terminal response")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify(f'AT^SSTK={pac_with_icon}',pac_with_icon,wait_for = tr_with_icon))
        test.expect(re.search(tr_with_icon, test.dut.at1.last_response))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Send a PAC of Send short message with alpha ID, check the Terminal response")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify(f'AT^SSTK={pac_with_alphaID}',pac_with_alphaID,wait_for =tr_with_alphaID,time_out=60))
        test.expect(re.search(tr_with_alphaID, test.dut.at1.last_response))


    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Restore to default configurations")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("CleanUp_2: Switch off SAT/URC")
        test.log.info("*******************************************************************")
        test.dut.at1.send_and_verify('AT^SCFG="SAT/URC","0"', ".*OK.*", timeout=30)



if (__name__ == "__main__"):
    unicorn.main()