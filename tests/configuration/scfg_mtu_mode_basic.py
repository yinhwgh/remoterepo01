#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0104186.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """ TC0104186.001    ScfgMtuModeBasic

    Test intention is to check AT^SCFG="GPRS/MTU/Mode" AT-Command

    1. Check AT^SCFG=? look for "GPRS/MTU/Mode" available values
    2. Check AT^SCFG? command and wait for correct response
    3. Set AT^SCFG="GPRS/MTU/Mode",1 command and wait for correct response
    4a. Check AT^SCFG? stored value
    4b. Check AT^SCFG="GPRS/MTU/Mode" stored value
    5. Restart module and check stored value
    6. Set AT^SCFG= "GPRS/MTU/Mode",0 command and wait for correct response
    7a. Check AT^SCFG? stored value
    7b. Check AT^SCFG="GPRS/MTU/Mode" stored value
    8. Restart module and check stored value
    9. Set AT^SCFG= "GPRS/MTU/Mode",<incorrect value>
    10. Check again all setting in Airplane mode
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.log.info('===== Check originally set value of nwmode parameter at test start =====')
        test.check_gprs_mtu_mode("OK")
        test.nwmode = re.search(r'.*"GPRS/MTU/Mode",(.*)', test.dut.at1.last_response)
        if test.nwmode[1]:
            test.log.info('Originally set value of nwmode parameter at test start: {}'.format(test.nwmode[1].strip()))
        else:
            test.log.info('Impossible to get originally set value of nwmode parameter at test start/r'
                          'nwmode parameter value: 1 will be set at the end of test')

    def run(test):
        for nwmode in [0, 1]:
            test.log.step('1. Check AT^SCFG=? look for "GPRS/MTU/Mode" available values')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG=?', '.*"GPRS/MTU/Mode",\\("0-1"\\).*OK.*'))
            test.log.step('2. Check AT^SCFG? command and wait for correct response')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG?', '.*"GPRS/MTU/Mode",(0|1).*OK.*'))
            test.log.step('3. Set AT^SCFG="GPRS/MTU/Mode",1 command and wait for correct response')
            test.set_gprs_mtu_mode('1', 'OK')
            test.log.step('4a. Check AT^SCFG? stored value')
            test.check_scfg('"GPRS/MTU/Mode",1.*OK')
            test.log.step('4b. Check AT^SCFG="GPRS/MTU/Mode" stored value')
            test.check_gprs_mtu_mode('"GPRS/MTU/Mode",1.*OK')
            test.log.step('5. Restart module and check stored value')
            test.expect(dstl_restart(test.dut))
            if nwmode == 1:
                dstl_set_airplane_mode(test.dut)
            test.check_gprs_mtu_mode('"GPRS/MTU/Mode",1.*OK')
            test.log.step('6. Set AT^SCFG="GPRS/MTU/Mode",0 command and wait for correct response')
            test.set_gprs_mtu_mode('0', 'OK')
            test.log.step('7a. Check AT^SCFG? stored value')
            test.check_scfg('"GPRS/MTU/Mode",0.*OK')
            test.log.step('7b. Check AT^SCFG="GPRS/MTU/Mode" stored value')
            test.check_gprs_mtu_mode('"GPRS/MTU/Mode",0.*OK')
            test.log.step('8. Restart module and check stored value')
            test.expect(dstl_restart(test.dut))
            if nwmode == 1:
                dstl_set_airplane_mode(test.dut)
            test.check_gprs_mtu_mode('"GPRS/MTU/Mode",0.*OK')
            test.log.step('9. Set AT^SCFG="GPRS/MTU/Mode",<incorrect value>')
            test.set_gprs_mtu_mode('2', 'CME ERROR')
            test.set_gprs_mtu_mode('-1', 'CME ERROR')
            test.set_gprs_mtu_mode('10', 'CME ERROR')
            test.set_gprs_mtu_mode('all', 'CME ERROR')
            if nwmode == 0:
                test.log.step('10. Check again all setting in Airplane mode')
                dstl_set_airplane_mode(test.dut)

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.log.info('Restore "GPRS/MTU/Mode",<nwmode> value')
        if test.nwmode[1]:
            test.set_gprs_mtu_mode(test.nwmode[1].strip(), 'OK')
        else:
            test.log.info('Originally set value of nwmode parameter at test start was impossible to get/r'
                          'nwmode parameter value: 1 will be set at the end of test')
            test.set_gprs_mtu_mode('1', 'OK')
        test.expect(test.dut.at1.send_and_verify('AT&F', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', '.*OK.*'))

    def set_gprs_mtu_mode(test, value, response):
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/MTU/Mode",{}'.format(value), '.*{}.*'.format(response)))

    def check_gprs_mtu_mode(test, response):
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/MTU/Mode"', '.*{}.*'.format(response)))

    def check_scfg(test, response):
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', '.*{}.*'.format(response)))


if "__main__" == __name__:
    unicorn.main()
