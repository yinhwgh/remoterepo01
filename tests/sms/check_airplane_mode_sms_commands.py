#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0103789.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address

class Test(BaseTest):
    """TC0103789.001    CheckAirplaneModeSmsCommands

    Check support of SMS-related commands while module is in Airplane Mode

    1. Enter Airplane mode (at+cfun=4),
    2. Enter SIM PIN if required,
    3. According to module's documentation verify support for each SMS-related AT command available (refer to "Short
     Message Service (SMS) Commands" section in AT command specification),
    3.1 Check each command format which is supported according to ATC (test, exec, read, write) - no need to check all
     parameters here.
    4. Return to Normal Functionality level (at+cfun=1).
    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CGSN", ".*OK.*"))
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CPMS=\"ME\",\"ME\",\"ME\"", ".*OK.*"))
        dstl_delete_all_sms_messages(test.dut)

    def run(test):
        test.log.step("1.  Enter Airplane mode (at+cfun=4).")
        test.expect(dstl_set_airplane_mode(test.dut))
        test.sleep(1)
        test.log.step("2. Enter SIM PIN if required.")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.log.step("3. According to module's documentation verify support for each SMS-related AT command available "
                      "(refer to \"Short Message Service (SMS) Commands\" section in AT command specification)")
        test.log.step("3.1 Check each command format which is supported according to ATC (test, exec, read, write) - "
                      "no need to check all parameters here.")
        if test.dut.platform.upper() == "QCT":
            test.log.info("For QCT please see IPIS100298750, IPIS100278432 or FUPs.")
        else:
            test.log.info("For others please see IPIS100268046 or FUPs.")
        test.expect(test.dut.at1.send_and_verify("AT+CMGF=?", ".*OK.*"))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMGF=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGW",'.*>.*', wait_for=".*>.*"))
        test.expect(test.dut.at1.send_and_verify('Test1',end="\u001A", expect=".*OK.*", timeout=20))
        test.expect(test.dut.at1.send_and_verify('AT+CMGW=\"{}\"'.format(test.dut.sim.int_voice_nr), '.*>.*',
                                                 wait_for=".*>.*"))
        test.expect(test.dut.at1.send_and_verify('Test2', end="\u001A", expect=".*OK.*", timeout=20))
        test.expect(test.dut.at1.send_and_verify("AT+CMGC=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGC=17,0", ".*ERROR.*"))
        if ">" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('Test Cmgc Error', end="\u001A", expect=".*OK|ERROR.*",
                                                     timeout=20))
        test.expect(test.dut.at1.send_and_verify("AT+CMGL=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGL", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGL=\"ALL\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGR=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGR=1", ".*OK.*"))
        if test.dut.product.upper() == ("ALAS5" or "PLPS9" or "EXS82"):
            test.expect(test.dut.at1.send_and_verify("AT+CMMS=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CMMS=0", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CMMS?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGS=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMGS=\"{}\"'.format(test.dut.sim.int_voice_nr), ".*ERROR.*"))
        if ">" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('Test Cmgs Error', end="\u001A", expect=".*OK|ERROR.*",
                                                     timeout=20))
        test.expect(test.dut.at1.send_and_verify("AT+CMSS=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMSS=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMA=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMA", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMA=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPMS=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPMS?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPMS=\"ME\",\"ME\",\"ME\"", ".*OK.*"))
        if test.dut.project.upper() == "BOBCAT":
            test.expect(test.dut.at1.send_and_verify("AT+CPNER=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPNER?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPNER=1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSCB=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSCB=1,\"3345\"", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSCB=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSCB=0,\"3345\"", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCMW=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify('AT^SCMW=\"{}\",,,1,3,8,34'.format(test.dut.sim.int_voice_nr),
                                                     '.*>.*', wait_for=".*>.*"))
            test.expect(test.dut.at1.send_and_verify('Test scmw', end="\u001A", expect=".*OK.*", timeout=20))
            test.expect(test.dut.at1.send_and_verify("AT^SCML=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCML", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCML=\"ALL\"", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCMR=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCMR=1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCMS=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify('AT^SCMS=\"{}\",,2,3,8,34'.format(test.dut.sim.int_voice_nr),
                                                     ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCA=?", ".*OK.*"))
        test.expect(dstl_set_sms_center_address(test.dut, '123124534'))
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", ".*OK.*"))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", ".*{}.*OK.*".format("\\" + test.dut.sim.sca_int)))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,21", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMGL=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMGL", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMGL=\"ALL\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMGR=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMGR=1", ".*OK.*"))
        if test.dut.platform.upper() == "QCT":
            test.expect(test.dut.at1.send_and_verify("AT^SSDA=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSDA=0", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSDA?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSDA=1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSDA?", ".*OK.*"))
        if test.dut.platform.upper() == "SQN":
            test.expect(test.dut.at1.send_and_verify("AT+CSAS=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSAS", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSAS=0", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CRES=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CRES", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CRES=1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSAS=0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGD=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGD=1", ".*OK.*"))
        test.log.step("4. Return to Normal Functionality level (at+cfun=1).")
        test.expect(dstl_set_full_functionality_mode(test.dut))

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
