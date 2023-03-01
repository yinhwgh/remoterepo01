#author: jin.li@thalesgroup.com
#location: Dalian
#TC0092097.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class Test(BaseTest):
    """
    TC0092097.001-TpAirplaneModeStoredInNv
    Subscribers: 1
    MCTest: Ture
    Debugged: Boxwood, Bobcat
    Intensioin: check whether cfun mode can be stored in NV when change setting of at^scfg="MeopMode/Cfun"
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at&f', expect='OK'))

    def run(test):
        test.log.info("1. Disable NV setting for<fun> in normal mode ")
        # Make sure NV setting is disable in normal mode
        test.expect(test.dut.at1.send_and_verify('at^Scfg?', '^SCFG: "MEopMode/CFUN","1","0"|"1"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MeopMode/Cfun","0"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MeopMode/Cfun","1"', expect='OK'))
        # set cfun as airplane mode
        test.expect(test.dut.at1.send_and_verify('AT+Cfun=4', waitfor='\^SYSSTART'))
        # Shut down and power on
        test.expect(test.dut.at1.send_and_verify("AT^SMSO",".*SHUTDOWN*", wait_for="SHUTDOWN"))
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board())

        test.expect(test.dut.at1.wait_for("\^SYSSTART"))
        # Check mode status should be normal
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1.*"))
        # Enable NV setting
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MeopMode/Cfun","0"', expect='OK'))
        # Set airplane mode and validate failed to register network and open socket service
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', waitfor='\^SYSSTART'))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('at+cops=0', expect='.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","IMS"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at^sica=1,1', expect='.*ERROR.*'))
        # Validate airplane mode should be kept after restart
        test.expect(test.dut.at1.send_and_verify("AT^SMSO",".*SHUTDOWN*", wait_for="SHUTDOWN"))
        test.sleep(2)
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
        test.expect(test.dut.at1.wait_for("\^SYSSTART"))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 4.*"))
        test.expect(test.dut.at1.send_and_verify('at^Scfg?', '^SCFG: "MEopMode/CFUN","0","4"'))

        test.log.info("2. Disable NV setting for<fun> in airplane mode ")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', expect='OK'))
        # Disable NV setting in airplane mode
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","1"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 4.*"))
        # Switch to normal mode
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', expect='OK'))
        # Shut down and power on to check mode should still be airplane mode
        test.expect(test.dut.at1.send_and_verify("AT^SMSO",".*SHUTDOWN*", wait_for="SHUTDOWN"))
        test.sleep(2)
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
        test.expect(test.dut.at1.wait_for("\^SYSSTART"))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 4.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', expect='^SCFG: "MEopMode/CFUN","1","4"'))
        # Enable NV
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MeopMode/Cfun","0"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', expect='OK'))
        # Shut down and power on to check mode should still be normal mode
        test.expect(test.dut.at1.send_and_verify("AT^SMSO", ".*SHUTDOWN*", wait_for="SHUTDOWN"))
        test.sleep(2)
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
        test.expect(test.dut.at1.wait_for("\^SYSSTART"))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', expect='^SCFG: "MEopMode/CFUN","0","1"'))
        #reset#
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MeopMode/Cfun","1"', expect='OK'))

        test.log.info("3. Enable NV setting in airplane mode ")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MeopMode/Cfun","0"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', expect='^SCFG: "MEopMode/CFUN","0","1"'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', expect='^SCFG: "MEopMode/CFUN","0","1"'))


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MeopMode/Cfun","1"', expect='OK'))
        test.expect(test.dut.dstl_restart())


if '__main__' == __name__:
    unicorn.main()
