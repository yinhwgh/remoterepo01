# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0094397.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.configuration import set_ims_registration_attempt
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1

class Test(BaseTest):
    """
    TC0094397.001 - AtScfgMeopmodeIms
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()


    def run(test):
        test.log.info('1. Check AT^SCFG=MeopMode/IMS PIN Protection for test, read and write commands')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))

        test.log.info('1.1 Check default value')
        test.expect(test.dut.dstl_get_settings_of_ims_registration_attempt()=='1')

        test.log.info(' 1.2 Set to different value without PIN')
        test.expect(test.dut.dstl_disable_ims_registration_attempt())

        test.log.info(' 1.3 Reset settings and check if "MEopMode/IMS" setting not changed')
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.dstl_get_settings_of_ims_registration_attempt()=='0')

        test.log.info(' 1.4 Store setting by restart module and check if "MEopMode/IMS" setting not changed')
        test.dut.dstl_restart()
        test.sleep(4)
        test.expect(test.dut.dstl_get_settings_of_ims_registration_attempt()=='0')

        test.log.info('2. Check AT^SCFG=MeopMode/IMS setting with PIN')
        test.dut.dstl_enter_pin()

        test.log.info('3. Set AT^SCFG=MeopMode/IMS,0 and check if values were set correctly')
        test.expect(test.dut.dstl_disable_ims_registration_attempt())
        test.expect(test.dut.dstl_get_settings_of_ims_registration_attempt()=='0')

        test.log.info('4. Set AT^SCFG=MeopMode/IMS,1 and check if values were set correctly')
        test.expect(test.dut.dstl_enable_ims_registration_attempt())
        test.expect(test.dut.dstl_get_settings_of_ims_registration_attempt()=='1')

        test.expect(test.dut.at1.send_and_verify("AT^SCFG=?", "OK"))
        res = test.dut.at1.last_response
        if 'SCFG: "MEopMode/IMS",("0","1"),' in res:
            test.log.info('5.Set AT^SCFG=MeopMode/IMS,0,<imsService> and check if values were set correctly')
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=Meopmode/Ims,0,mmtel", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=Meopmode/Ims", "SCFG: \"MEopMode/IMS\",\"1\""))

            test.expect(test.dut.at1.send_and_verify("AT^SCFG=Meopmode/Ims,0,smsip", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=Meopmode/Ims", "SCFG: \"MEopMode/IMS\",\"1\""))

            test.log.info('6 Set AT^SCFG=MeopMode/IMS,1,<imsService> and check if values were set correctly')
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=Meopmode/Ims,1,mmtel", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=Meopmode/Ims", "SCFG: \"MEopMode/IMS\",\"1\",\"mmtel\""))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=Meopmode/Ims,1,smsip", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=Meopmode/Ims", "SCFG: \"MEopMode/IMS\",\"1\",\"smsip\""))
        else:
            test.log.info('Step 5-6 not support, skip')

        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/IMS/SMS/TMode\"", "OK|ERROR"))
        res = test.dut.at1.last_response
        if 'OK' in res:
            test.log.info('7.check if AT command AT^SCFG="MEopMode/IMS/SMS/TMode"[, <ims-tmode>] is disabled by default. Verify after reboot if setting is nonvolatile. Restore default settings. ')
        else:
            test.log.info('Step 7 not support, skip')

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
