#responsible: kamil.kedron@globallogic.com
#location: Wroclaw
#TC0091735.004

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.status_control.sind_parameters import dstl_get_sind_read_response_dict
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.delete_sms import dstl_delete_sms_message_from_index
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.sms_functions import dstl_send_sms_message, dstl_enable_sms_urc
from dstl.call.setup_voice_call import dstl_release_call
from dstl.auxiliary.check_urc import dstl_check_urc


class Test(BaseTest):
    """
    INTENTION
    Check the status for indicator "smsfull" in following situations:
    - during voice call
    - in idle state

    PRECONDITION
    Use 3 modules with SIM card.
    1. Set modules to factory defaults.
    2. Delete all SMS from ME and SM storage.
    3. Deactivate all other indicators not used in this test.
    4. Set SMS Text Mode for DUT and Remote_2.
    5. Set Service Center Address for DUT and Remote_2.
    6. Set CNMI URC indication.

    EXPECTED RESULTS
    The status of indicator "+CIEV: smsfull" is output according to AT^SIND settings: - "+CIEV: smsfull, 1"
    if SMS storage was completely filled.
    """
    def setup(test):
        test.time_value = 5
        test.wait_time_value = 90
        test.enable_state = 1
        test.disable_state = 0
        test.test_sind = "smsfull"
        test.sms_message = "The quick brown fox jumps over the lazy dog"
        test.dut_phone_num = test.dut.sim.nat_voice_nr

        for interface in [test.dut, test.r1, test.r2]:
            test.set_precondition(interface)
            test.log.step('Precondition: 1. Set modules to factory defaults.')
            test.expect(interface.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
            test.expect(interface.at1.send_and_verify("AT&W", ".*OK.*", timeout=test.time_value))

        if not test.dut.at1.send_and_verify("AT^SIND?", ".*SIND: smsfull,.*OK.*"):
            test.expect(False, critical=True,
                        msg=f"Product {test.dut.product} does not support AT^SIND= 'smsfull', scripts exit")

        test.log.step('Precondition: 2. Delete all SMS from ME and SM storage.')
        for sms_memory in ["ME", "SM"]:
            test.expect(dstl_set_preferred_sms_memory(test.dut, sms_memory))
            test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('Precondition: 3. Deactivate all other indicators not used in this test.')
        sind_dict = dstl_get_sind_read_response_dict(test.dut)
        for sind_key, sind_value in sind_dict.items():
            test.dut.at1.send_and_verify(f'AT^SIND="{sind_key}",0', ".*OK|ERROR.*")

        test.log.step('Precondition: 4. Set SMS Text Mode for DUT and Remote_2.')
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r2))

        test.log.step('Precondition: 5. Set Service Center Address for DUT and Remote_2.')
        test.expect(dstl_set_sms_center_address(test.dut))
        test.expect(dstl_set_sms_center_address(test.r2))

        test.log.step('Precondition: 6. Set CNMI URC indication.')
        test.expect(dstl_enable_sms_urc(test.dut))

    def run(test):
        test.log.step('1. Enable the "smsfull" indicator with SIND command for the test')
        test.expect(test.set_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' is not enabled")

        test.log.step('2. Check "smsfull" indicator. Should be activated')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' is not activated")

        test.log.step('3. Set SMS storage to "ME" and write SMS until storage is one sms before full.')
        test.write_sms_to_memory("ME")

        test.log.step('4. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' status changed before last sms saved to storage")

        test.log.step('5. Check smsfull_during idle state for write sms to "ME" storage.')
        test.check_smsfull_during_idle("ME", "Write", 5)

        test.log.step('6. Check smsfull_during voice call state for write sms to "ME" storage.')
        test.check_smsfull_during_call("ME", "Write", 6)

        test.log.step('7. Set SMS storage to "SM" and write SMS until storage is one sms before full.')
        test.write_sms_to_memory("SM")

        test.log.step('8. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' status changed before last sms saved to storage")

        test.log.step('9. Check smsfull_during idle state for received sms to "SM" storage.')
        test.check_smsfull_during_idle("SM", "Send", 9)

        test.log.step('10. Check smsfull_during voice call state for received sms to "SM" storage.')
        test.check_smsfull_during_call("SM", "Send", 10)

        test.log.step('11. Disable the "smsfull" indicator with SIND command for the test.')
        test.expect(test.set_status_sind(test.test_sind, test.disable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' is not deactivated")

        test.log.step('12. Delete all SMS from ME and SM storage.')
        for sms_memory in ["ME", "SM"]:
            test.expect(dstl_set_preferred_sms_memory(test.dut, sms_memory))
            test.expect(dstl_delete_all_sms_messages(test.dut))

    def cleanup(test):
        test.log.info('Delete all SMS from ME and SM storage.')
        for sms_memory in ["ME", "SM"]:
            test.expect(dstl_set_preferred_sms_memory(test.dut, sms_memory))
            test.expect(dstl_delete_all_sms_messages(test.dut))
        for interface in [test.dut.at1, test.r1.at1, test.r2.at1]:
            test.expect(interface.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
            test.expect(interface.send_and_verify("AT&W", ".*OK.*", timeout=test.time_value))

    def write_sms_to_memory(test, memory):
        test.expect(dstl_set_preferred_sms_memory(test.dut, memory))
        for mem_num in range(dstl_get_sms_count_from_memory(test.dut)[2],
                             int(dstl_get_sms_memory_capacity(test.dut, 3)) - 1):
            test.expect(dstl_write_sms_to_memory(test.dut))

    def set_precondition(test, interface):
        dstl_detect(interface)
        dstl_get_imei(interface)
        dstl_get_bootloader(interface)
        test.expect(dstl_register_to_network(interface))

    def set_status_sind(test, sind_param, sind_mode, sind_ind=0):
        return test.dut.at1.send_and_verify(f'AT^SIND="{sind_param}",{sind_mode}',
                                            f'.*SIND: {sind_param},{sind_mode},{sind_ind}.*OK.*')

    def get_status_sind(test, sind_param, exp_sind, sind_ind):
        return test.dut.at1.send_and_verify(f'AT^SIND="{sind_param}",2',
                                            f'.*SIND: {sind_param},{exp_sind},{sind_ind}.*OK.*')

    def execute_voice_call(test):
        test.expect(test.dut.at1.send_and_verify("ATS0=1", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify(f"ATD{test.dut_phone_num};", ".*OK.*"))
        test.expect(test.dut.at1.wait_for("RING", timeout=60))
        test.expect(test.dut.at1.send_and_verify("ATA", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0.*OK.*"))
        test.expect(test.r1.at1.send_and_verify_retry("AT+CLCC", expect="\+CLCC: 1,0,0.*OK.*", retry=3,
                                                      timeout=5, wait_after_send=0, end="\r", append=False))

    def check_and_disconnect_call(test):
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0.*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0.*OK.*"))
        test.expect(dstl_release_call(test.r1))
        test.expect(dstl_release_call(test.dut))

    def check_smsfull_during_call(test, sms_memory, sms_action, step_count):
        test.log.step(f'{step_count}.1. Start voice call from Remote_1 to DUT.')
        test.execute_voice_call()
        test.check_smsfull_during_idle(sms_memory, sms_action, f'{step_count}.1')
        test.log.step(f'{step_count}.2. Disconnect voice call.')
        test.check_and_disconnect_call()

    def check_smsfull_during_idle(test, sms_memory, sms_action, step_count):
        if sms_action is "Send":
            test.log.step(f'{step_count}.1. Send one last SMS from Remote_2 to DUT.')
            test.expect(dstl_send_sms_message(test.r2, test.dut.sim.nat_voice_nr, test.sms_message))
            test.expect(dstl_check_urc(test.dut, "CMTI", append=True, timeout=test.wait_time_value))
        else:
            test.log.step(f'{step_count}.1. Write one last SMS to storage.')
            test.expect(dstl_write_sms_to_memory(test.dut))

        test.log.step(f'{step_count}.2. Check if "smsfull" URC was received.')
        test.expect(test.dut.at1.wait_for("CIEV: smsfull,1", append=True), msg="Failed: CIEV: smsfull,1 not occurred")

        test.log.step(f'{step_count}.3. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.enable_state),
                    msg="Failed: AT^SIND= 'smsfull' status not changed after last sms saved to storage")

        test.log.step(f'{step_count}.4. Delete one SMS from "{sms_memory}" storage.')
        test.expect(dstl_delete_sms_message_from_index(test.dut,0))

        test.log.step(f'{step_count}.5. Check if "smsfull" URC was received.')
        test.expect(test.dut.at1.wait_for("CIEV: smsfull,0", append=True), msg="Failed: CIEV: smsfull,0 not occurred")

        test.log.step(f'{step_count}.6. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' status not changed after one sms was deleted from storage")


if "__main__" == __name__:
    unicorn.main()