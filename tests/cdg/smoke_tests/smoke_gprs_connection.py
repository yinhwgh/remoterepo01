# responsible: kamil.mierzwa@globallogic.com
# location: Wroclaw

import re
import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_umts, dstl_register_to_gsm, dstl_register_to_lte, dstl_register_to_network
from dstl.packet_domain.ps_attach_detach import dstl_ps_attach, dstl_ps_detach
from dstl.packet_domain.pdp_activate_deactivate import dstl_pdp_activate, dstl_pdp_deactivate
from dstl.configuration.scfg_radio_band import dstl_get_radio_band

class Test(BaseTest):
    """
    Main goal is to check if GPRS works correctly
    1. Log DUT to network to 3G
    2. Do PS attach (AT+CGATT=1)
    3. Check if connection is set up
    4. Set CGDCONT
    5. Activate PDP context (AT+CGACT=1,1)
    6. Check if PDP context is active
    7. Deactivate PDP context
    8. Check if PDP context is active
    9. Do PS detach
    10. Check if connection is set up
    """

    def setup(test):
        test.cid = 1
        test.apn = test.dut.sim.apn_v4
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_check_c_revision_number(test.dut)

    def run(test):
        test.log.step("1. register module to the network")
        if dstl_get_radio_band(test.dut, "2G"):
            test.expect(dstl_register_to_gsm(test.dut))
        elif dstl_get_radio_band(test.dut, "3G"):
            test.expect(dstl_register_to_umts(test.dut))
        else:
            test.cid = 3
            test.expect(dstl_register_to_lte(test.dut))

        test.log.step(f"2. set appropriate apn value for cid={test.cid}")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGDCONT={test.cid},\"IP\",\"{test.apn}\"", ".*OK.*"))

        test.log.step("3. attach DUT to packet domain service => PS attach")
        dstl_ps_attach(test.dut)
        test.expect(re.search("\+CGATT: 1", test.dut.at1.last_response))

        test.log.step(f"4. activate pdp context for cid={test.cid} ")
        dstl_pdp_activate(test.dut, test.cid)
        test.expect(re.search(f"\+CGACT: {test.cid},1", test.dut.at1.last_response))

        test.log.step("5. deactivate pdp for cid={test.cid} ")
        dstl_pdp_deactivate(test.dut, test.cid)
        test.expect(re.search(f"\+CGACT: {test.cid},0", test.dut.at1.last_response))

        test.log.step("6. detach DUT from packet domain service => PS detach")
        dstl_ps_detach(test.dut)
        test.expect(re.search("\+CGATT: 0", test.dut.at1.last_response))

    def cleanup(test):
        test.expect(dstl_register_to_network(test.dut))



if "__main__" == __name__:
    unicorn.main()