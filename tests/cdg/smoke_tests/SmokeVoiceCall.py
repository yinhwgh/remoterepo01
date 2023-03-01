# responsible: kamil.mierzwa@globallogic.com
# location: Wroclaw

import re
import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import  dstl_register_to_network
from dstl.call.setup_voice_call import dstl_mt_voice_call_by_number, dstl_voice_call_by_number, dstl_release_call, dstl_check_voice_call_status_by_clcc

class Test(BaseTest):
    """
    main goal is to check if voice call works correctly.
    1. Log DUT and REMOTE to network
    2. Call from DUT to REMOTE
    3. Disconnect connection
    4. Call from REMOTE to DUT
    5. Disconnect connection
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        if (test.dut.project not in test.voice_call_supporting) or (test.dut.project == 'Boxwood' and test.dut.step != 3):
            test.expect(False, critical=True, msg=f"DUT=={test.dut.project} and doesn't support voice call functionality")
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        if test.r1.project not in test.voice_call_supporting:
            test.expect(False, critical=True, msg = f"REMOTE=={test.r1.project} and doesn't support voice call functionality")

    def run(test):
        test.log.step("1. Register DUT to the network ")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Register REMOTE to the network ")
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("3. establish MO call DUT ==> REMOTE ")
        test.expect(dstl_voice_call_by_number(test.dut, test.r1, test.r1.sim.nat_voice_nr))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+clcc", ".*OK.*"))
        test.expect(re.search(f"\+CLCC: 1,0,0,0,0,\"{test.r1.sim.nat_voice_nr}\",(128|129|145|161|255)", test.dut.at1.last_response))
        test.expect(dstl_release_call(test.r1))
        test.sleep(5)

        test.log.step("4. establish MT call REMOTE ==> DUT ")
        test.expect(dstl_mt_voice_call_by_number(test.dut, test.r1, test.dut.sim.nat_voice_nr))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+clcc", ".*OK.*"))
        test.expect(re.search(f"\+CLCC: 1,1,0,0,0,\"{test.r1.sim.nat_voice_nr}\",(128|129|145|161|255)", test.dut.at1.last_response))
        test.expect(dstl_release_call(test.dut))
        test.sleep(5)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
