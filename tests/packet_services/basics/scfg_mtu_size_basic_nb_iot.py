#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC 0104968.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_minimum_functionality_mode, dstl_set_full_functionality_mode
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_nbiot


class Test(BaseTest):
    """responsible: Dariusz Drozdek, dariusz.drozdek@globallogic.com
    # Wroclaw

    # TC 0104968.001    ScfgMtuSizeBasicNBIoT

    Intention of this TC is to check behaviour of AT^SCFG="GPRS/MTU/Size" command in NB-IoT network.

    1. Register module to NB-IoT network
    2. Check AT^SCFG=? and look for "GPRS/MTU/Size" supported values
    3. Check AT^SCFG? command to check "GPRS/MTU/Size" actual value
    4. Check AT^SCFG="GPRS/MTU/Size" actual stored value
    5. Try to set some values different than default one for NBIot AT^SCFG="GPRS/MTU/Size","value"
    6. Check AT^SCFG? command to check "GPRS/MTU/Size" value
    7. Check AT^SCFG="GPRS/MTU/Size" stored value
    8. Restart module and check "GPRS/MTU/Size" stored value
    9. Enter PIN and active PDP context (if it is not) then check stored value again.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Mode\",1", ".*OK.*"))
        test.sleep(1)
        test.expect(dstl_restart(test.dut))

    def run(test):
        test.log.step("1. Register module to NB-IoT network")
        test.expect(dstl_register_to_nbiot(test.dut))
        test.log.step("2. Check AT^SCFG=? and look for \"GPRS/MTU/Size\" supported values")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=?", ".*OK.*"))
        test.expect(re.search(r"\"GPRS\/MTU\/Size\",\(\"1280-1500\"\)", test.dut.at1.last_response))
        test.log.step("3. Check AT^SCFG? command to check \"GPRS/MTU/Size\" actual value")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?", ".*\"GPRS/MTU/Size\",1358.*OK.*"))
        test.log.step("4. Check AT^SCFG=\"GPRS/MTU/Size\" actual stored value")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\"", ".*\"GPRS/MTU/Size\",1358.*OK.*"))
        test.log.step(
            "5. Try to set some values different than default one for NBIot AT^SCFG=\"GPRS/MTU/Size\",\"value\"")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\",1300", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\",1400", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\",1420", ".*ERROR.*"))
        test.log.step("6. Check AT^SCFG? command to check \"GPRS/MTU/Size\" value")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?", ".*\"GPRS/MTU/Size\",1358.*OK.*"))
        test.log.step("7. Check AT^SCFG=\"GPRS/MTU/Size\" stored value")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\"", ".*\"GPRS/MTU/Size\",1358.*OK.*"))
        test.log.step("8. Restart module and check \"GPRS/MTU/Size\" stored value")
        test.expect(dstl_restart(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?", ".*\"GPRS/MTU/Size\",1358.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\"", ".*\"GPRS/MTU/Size\",1358.*OK.*"))
        test.log.step("9. Enter PIN and active PDP context (if it is not) then check stored value again.")
        test.expect(dstl_register_to_nbiot(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 1,1.*OK.*"))
        if ('CGACT: 1,0' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?", ".*\"GPRS/MTU/Size\",1358.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\"", ".*\"GPRS/MTU/Size\",1358.*OK.*"))

    def cleanup(test):
        dstl_set_minimum_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\",1430", ".*OK.*"))
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
