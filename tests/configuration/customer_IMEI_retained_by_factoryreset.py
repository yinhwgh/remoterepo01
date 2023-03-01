#author: yandong.wu@thalesgroup.com
#location: Dalian
#TC0104492.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_identification import dstl_get_bootloader

class Test(BaseTest):
    '''
       TC0104492.001 - CustomerIMEIRetainedByFactoryReset
       Intention: This test case is design to check whether customer IMEI is retain after the AT command AT^SCFG="MEopMode/Factory","all".
                  This TC can be conduct only by person, which has access to module without already set customer IMEI.
       Precondition:  In order to run the following script, customer IMEI must be input into the module beforehand.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(3)

    def run(test):
        test.log.info('1. Set AT^SCFG="MEopMode/Factory","none" and restart the module.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=\"MEopMode/Factory\",none', 'OK'))

        test.log.step("2.Display serial number. ")
        test.expect(test.dut.at1.send_and_verify("AT^SGSN", "OK"))

        test.log.step('3.Display IMEI ')
        test.expect(test.dut.at1.send_and_verify("AT^SGSN?", "OK"))
        res1 = test.dut.at1.last_response

        test.log.step('4.Enter PIN')
        test.expect(dstl_enter_pin(test.dut))

        test.log.info('5. Execute AT^SCFG="MEopMode/Factory","all", restart module.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=\"MEopMode/Factory\",all', 'OK', wait_for='SYSSTART', timeout=30))

        test.log.step('6.Check if customer IMEI has been kept unchanged. ')
        test.expect(test.dut.at1.send_and_verify("AT^SGSN?", "OK"))
        res2 = test.dut.at1.last_response
        test.expect(res1 in res2)

    def cleanup(test):
        pass

if "__main__" == __name__:
   unicorn.main()