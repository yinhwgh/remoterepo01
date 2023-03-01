# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0104489.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration import reset_to_factory_default_state

class Test(BaseTest):
    '''
    TC0104489.001 - UserConfigurationDeletedByFactoryReset
    This test case is design to check whether user configuration are deleted
    after the AT command AT^SCFG="MEopMode/Factory","all"

    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(3)

    def run(test):
        test.log.info('1. Set AT^SCFG="MEopMode/Factory","none" and restart the module.')
        test.expect(test.dut.at1.send_and_verify('at^scfg=\"MEopMode/Factory\",none', 'OK'))
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_enter_pin()
        test.sleep(3)

        if test.dut.project == 'VIPER':
            #as IPIS set to not_to_fix, only check sics and siss
            try:
                test.dut.usb_m.send_and_verify("AT",'OK')
            except:
                test.expect(False, critical=True, msg='Need connect usb_m port to quit sleep mode.')
            test.viper_step()
        else:
            test.log.info(
                '2. Change parameters of AT+CGDCONT, AT^SGAUTH commands to non-default values, restart module')
            test.expect(test.dut.at1.send_and_verify('at+cgdcont=5,\"IP\",\"DUMMYAPN\"'))
            test.expect(test.dut.at1.send_and_verify('at^sgauth=5,0'))

            test.log.info(
                '3. Check if the parameters values of above commands were retained after the restart of the module')
            test.dut.dstl_restart()
            test.sleep(5)
            test.dut.dstl_enter_pin()
            test.sleep(3)
            test.expect(test.dut.at1.send_and_verify('at+cgdcont?', 'CGDCONT: 5,\"IP\",\"DUMMYAPN\"'))
            test.expect(test.dut.at1.send_and_verify('at^sgauth?', 'SGAUTH: 5,0'))

            test.log.info('4. Execute AT^SCFG="MEopMode/Factory","all"')
            test.expect(test.dut.dstl_reset_to_factory_default())

            test.log.info('5. Check if the parameters have been reset to default values')
            test.expect(test.dut.at1.send_and_verify('at+cgdcont?', 'CGDCONT: 5,\"IP\",\"DUMMYAPN\"') == False)
            test.expect(test.dut.at1.send_and_verify('at^sgauth?', 'SGAUTH: 5,0') == False)

    def cleanup(test):
        pass

    def viper_step(test):
        test.log.info('2. Change parameters of at^sics,at^siss commands')
        test.expect(test.dut.at1.send_and_verify('at^sics=1,"dns1","8.8.8.8"'))
        test.expect(test.dut.at1.send_and_verify('at^siss=1,srvtype,socket'))
        test.log.info(
            '3. Check if the parameters values of above commands were retained after the restart of the module')
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_enter_pin()
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at^sics?', 'SICS: 1,"dns1","8.8.8.8"'))
        test.expect(test.dut.at1.send_and_verify('at^siss?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siss=1,srvtype,socket'))

        test.log.info('4. Execute AT^SCFG="MEopMode/Factory","all"')
        test.expect(test.dut.dstl_reset_to_factory_default())
        test.log.info('5. Check if the parameters have been reset to default values')
        test.expect(test.dut.at1.send_and_verify('at^sics?', 'SICS: 1,"dns1","8.8.8.8"') == False)
        test.expect(test.dut.at1.send_and_verify('at^siss?', 'SISS: 1,"srvType","Socket"') == False)


if "__main__" == __name__:
    unicorn.main()
