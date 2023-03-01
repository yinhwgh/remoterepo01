# responsible: dan.liu@thalesgroup.com
# location: Dalian
# TC0095660.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.devboard import devboard
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.identification.get_imei import dstl_get_imei
from core import dstl



class Test(BaseTest):
    """

    TC0095660.001 - Ring0BusyComm

    Test intention : Check functionality of RING0 line of busy communication interface.

    """

    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.r1.dstl_detect()
        test.dut.devboard.send_and_verify('MC:URC=OFF', 'OK')
        if test.dut.project.upper() == "COUGAR|BOXWOOD|VIPER":
            # Setting takes effect after next restart.:
            test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","std"', 'OK')
            test.dut.dstl_restart()

        else:
            pass
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","local"', 'OK')
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime",2', 'OK')
        test.dut.dstl_restart()
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline"', '.*local.*')
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime"', '.*2.*')
        pass

    def run(test):
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()
        test.r1.dstl_enter_pin()
        test.r1.dstl_register_to_network()
        test.r1.dstl_select_sms_message_format(sms_format='Text')
        test.dut.dstl_select_sms_message_format(sms_format='Text')
        test.dut.devboard.send_and_verify('MC:URC=Ringline', 'OK')
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="SM","SM","SM"'))
        test.dut.dstl_delete_all_sms_messages()
        test.dut.at1.send_and_verify('AT+CNMI=2,1', 'OK')
        test.issue_ringline_local_by_sms()
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","off"', 'OK')
        test.dut.dstl_restart()
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline"', '.*off.*')
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()
        test.r1.dstl_enter_pin()
        test.r1.dstl_register_to_network()
        test.r1.dstl_select_sms_message_format(sms_format='Text')
        test.dut.dstl_select_sms_message_format(sms_format='Text')
        test.dut.devboard.send_and_verify('MC:URC=Ringline', 'OK')
        pass

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="SM","SM","SM"'))
        test.dut.dstl_delete_all_sms_messages()
        test.dut.at1.send_and_verify('AT+CNMI=2,1', 'OK')
        test.issue_ringline_off_by_sms()
        pass

    def issue_ringline_local_by_sms(test):
        test.expect(test.r1.at1.send_and_verify('at+cmgs="{}"'.format(test.dut.sim.nat_voice_nr), '>', wait_for='>'))
        test.expect(test.r1.at1.send_and_verify('HI\x1A', "OK"))
        test.expect(test.devboard_check_urc())
        return

    def issue_ringline_off_by_sms(test):
        test.expect(test.r1.at1.send_and_verify('at+cmgs="{}"'.format(test.dut.sim.nat_voice_nr), '>', wait_for='>'))
        test.expect(test.r1.at1.send_and_verify('HI\x1A', "OK"))
        test.expect(test.devboard_check_urc() is False)
        return

    def devboard_check_urc(test, expect_urc='>URC:  RINGline: 0', append=True, timeout=30):
        response = test.dut.devboard.last_response
        """Check urc in last response, if not exist, wait for specified time until expect_urc appears"""
        if response:
            appeared = test.dut.devboard.verify(expect_urc, response)
            test.log.info(f"URC {expect_urc} exists in last response: {appeared}")
            if not appeared:
                appeared = test.dut.devboard.wait_for(expect_urc, append=append, timeout=timeout)
                return appeared

        return False


if "__main__" == __name__:
    unicorn.main()
