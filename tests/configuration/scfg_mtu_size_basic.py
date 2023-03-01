#responsible sebastian.lupkowski@globallogic.com
#Wroclaw
#TC 0104187.001
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
import random


class Test(BaseTest):
    """author: Sebastian Lupkowski, sebastian.lupkowski@globallogic.com, location: Wroclaw

    TC0104187.001    ScfgMtuSizeBasic

    Test intention is to check AT^SCFG="GPRS/MTU/Size" AT-Command

    1. Check AT^SCFG=? look for "GPRS/MTU/Size" available values
    2a. Check AT^SCFG? command and wait for correct response
    2b. Check AT^SCFG= "GPRS/MTU/Size" stored value
    3. Set AT^SCFG="GPRS/MTU/Size",<mtusize> command and wait for correct response (min supported value of <mtusize>)
    4a. Check AT^SCFG? stored value
    4b. Check AT^SCFG= "GPRS/MTU/Size" stored value
    5. Set AT^SCFG="GPRS/MTU/Size", <mtusize> command and wait for correct response (max supported value of <mtusize>)
    6a. Check AT^SCFG? stored value
    6b. Check AT^SCFG= "GPRS/MTU/Size" stored value
    7. Restart module and check stored value
    8. Set AT^SCFG="GPRS/MTU/Size",<random value from whole supported range except 1430> command and wait for
    correct response
    9a. Check AT^SCFG? stored value
    9b. Check AT^SCFG= "GPRS/MTU/Size" stored value
    10. Set AT^SCFG="GPRS/MTU/Size",<incorrect value> command and wait for correct response
    11. Check again all setting in Airplane mode
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        i = 0
        while i < 2:
            test.log.step("1. Check AT^SCFG=? look for \"GPRS/MTU/Size\" available values ")
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=?", ".*\"GPRS/MTU/Size\",\\(\"1280-1500\"\\).*OK.*"))
            test.log.step("2a. Check AT^SCFG? command and wait for correct response")
            check_scfg(test, "\"GPRS/MTU/Size\",(128[0-9]|129[0-9]|1[3-9][0-9]{2}|[23][0-9]{3}|40[0-8][0-9]|409[0-6])"
                             ".*OK.*")
            test.log.step("2b. Check AT^SCFG= \"GPRS/MTU/Size\" stored value")
            check_gprs_mtu_size(test, "\"GPRS/MTU/Size\",(128[0-9]|129[0-9]|1[3-9][0-9]{2}|[23][0-9]{3}|40[0-8][0-9]"
                                      "|409[0-6]).*OK")
            test.log.step("3. Set AT^SCFG=\"GPRS/MTU/Size\",<mtusize> command and wait for correct response "
                          "(min supported value of <mtusize>)")
            set_gprs_mtu_size(test, '1280', 'OK')
            test.log.step("4a. Check AT^SCFG? stored value ")
            check_scfg(test, '.*\"GPRS/MTU/Size\",1280.*OK.*')
            test.log.step("4b. Check AT^SCFG=\"GPRS/MTU/Size\" stored value")
            check_gprs_mtu_size(test, '.*\"GPRS/MTU/Size\",1280.*OK.*')
            test.log.step("5. Set AT^SCFG=\"GPRS/MTU/Size\", <mtusize> command and wait for correct response"
                          " (max supported value of <mtusize>)")
            set_gprs_mtu_size(test, '1500', 'OK')
            test.log.step("6a. Check AT^SCFG? stored value ")
            check_scfg(test, '.*\"GPRS/MTU/Size\",1500.*OK.*')
            test.log.step("6b. Check AT^SCFG=\"GPRS/MTU/Size\" stored value")
            check_gprs_mtu_size(test, '.*\"GPRS/MTU/Size\",1500.*OK.*')
            test.log.step("7. Restart module and check stored value")
            test.expect(dstl_restart(test.dut))
            if i is 1:
                dstl_set_airplane_mode(test.dut)
            test.sleep(10)  # waiting for module to get ready
            check_gprs_mtu_size(test, '.*\"GPRS/MTU/Size\",1500.*OK.*')
            check_scfg(test, '.*\"GPRS/MTU/Size\",1500.*OK.*')
            test.log.step("8. Set AT^SCFG=\"GPRS/MTU/Size\",<random value from whole supported range except 1430> "
                          "command and wait for correct response")
            random_value = str(random.randint(1281, 1499))
            set_gprs_mtu_size(test, random_value, 'OK')
            test.log.step("9a. Check AT^SCFG? stored value ")
            check_scfg(test, '.*\"GPRS/MTU/Size\",{}.*OK.*'.format(random_value))
            test.log.step("9b. Check AT^SCFG=\"GPRS/MTU/Size\" stored value")
            check_gprs_mtu_size(test, '.*\"GPRS/MTU/Size\",{}.*OK.*'.format(random_value))
            test.log.step("10. Set AT^SCFG=\"GPRS/MTU/Size\",<incorrect value> command and wait for correct response")
            set_gprs_mtu_size(test, '1279', 'ERROR')
            set_gprs_mtu_size(test, '1501', 'ERROR')
            set_gprs_mtu_size(test, '1430a', 'ERROR')
            set_gprs_mtu_size(test, '4097', 'ERROR')
            set_gprs_mtu_size(test, '0', 'ERROR')
            set_gprs_mtu_size(test, 'all', 'ERROR')
            set_gprs_mtu_size(test, 'max', 'ERROR')
            set_gprs_mtu_size(test, 'min', 'ERROR')
            if i is 0:
                test.log.step("11. Check again all setting in Airplane mode")
                dstl_set_airplane_mode(test.dut)
            i += 1

    def cleanup(test):
        set_gprs_mtu_size(test, '1430', 'OK')
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def set_gprs_mtu_size(test, value, response):
    test.expect(test.dut.at1.send_and_verify('AT^SCFG=\"GPRS/MTU/Size\",{}'.format(value), '.*{}.*'.format(response)))


def check_gprs_mtu_size(test, response):
    test.expect(test.dut.at1.send_and_verify('AT^SCFG=\"GPRS/MTU/Size\"', '.*{}.*'.format(response)))


def check_scfg(test, response):
    test.expect(test.dut.at1.send_and_verify('AT^SCFG?', '.*{}.*'.format(response)))


if "__main__" == __name__:
    unicorn.main()
