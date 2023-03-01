#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0102351.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_gsm, dstl_register_to_umts


class Test(BaseTest):
    """TC0102351.001    PdpContextDefineAndActivate

    Check if it is possible to define all (according to ATspec) PDP contexts and activate at least two of them.

    1. Define all possible PDP contexts (according to ATspec).
    2. Activate PDP context for CID 1 and 2.
    3. Check state of all PDP contexts.
    4. Deactivate  PDP context for CID 1 and 2.
    5. Check state of all PDP contexts.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        project = test.dut.project.upper()
        if project == "SERVAL":
            dstl_register_to_gsm(test.dut)
        else:
            if dstl_register_to_gsm(test.dut) is True:
                test.log.info("module registered to 2G")
            else:
                test.log.info("module not registered to 2G, trying to register to 3G")
                dstl_register_to_umts(test.dut)
        test.sleep(10)

    def run(test):
        test.log.step("1. Define all possible PDP contexts (according to ATspec).")
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,\"IP\",\"{}\"'.format(test.dut.sim.apn_v4),
                                                 ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,\"IP\",\"{}\"'.format(test.dut.sim.apn_public_v4),
                                                 ".*OK.*"))
        for cid in range(3, 17):
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT={},\"IP\",\"internet{}\"".format(cid, cid), ".*OK.*"))
        test.sleep(5)
        test.log.step("2. Activate PDP context for CID 1 and 2.")
        for cid in range(1, 3):
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,{}".format(cid), ".*OK.*"))
            test.sleep(1)
        test.log.step("3. Check state of all PDP contexts.")
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*OK.*"))
        test.expect(re.search(r".*\+CGACT: 1,1.*\n.*\+CGACT: 2,1.*", test.dut.at1.last_response))
        for cid in range(3, 17):
            test.expect(re.search(r".*\+CGACT: {},0".format(cid), test.dut.at1.last_response))
        test.log.step("4. Deactivate  PDP context for CID 1 and 2.")
        for cid in range(1, 3):
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,{}".format(cid), ".*OK.*"))
        test.sleep(1)
        test.log.step("5. Check state of all PDP contexts.")
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*OK.*"))
        for cid in range(1, 17):
            test.expect(re.search(r".*\+CGACT: {},0".format(cid), test.dut.at1.last_response))

    def cleanup(test):
        for cid in range(3, 17):
            test.dut.at1.send_and_verify("AT+CGDCONT={}".format(cid), ".*OK.*")
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
