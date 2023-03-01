# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0092550.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import check_urc

import re


class Test(BaseTest):
    """
    TC0092550.001 - TpAtSlccBasic
    Intention: This procedure provides basic tests for the test and write command of AT^SLCC.
    Subscriber: 2
    """

    def setup(test):
        test.log.info("********** Set DUT to SIM PIN status ************")
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

        test.log.info("********** Set remote module be ready for call ************")
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())

        test.log.info("********** Detect if Module supports AT+CPAS command ************")
        test.dut.at1.send_and_verify("AT+CPAS", "OK|ERROR")
        if 'OK' in test.dut.at1.last_response:
            test.cpas_check = True
        else:
            test.cpas_check = False

    def run(test):
        test_res = "\^SLCC: \(0-1\)\s+OK"
        exec_res = "AT\^SLCC\s+OK\s+"  # Only ATC echo and OK in response

        test.log.step('1. Test, Read, write and exec command without PIN')
        # Configuration need be added to local.cfg or dstl if AT^SLCC is pin protected for some products
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '\+CPIN: SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SLCC=?', test_res))
        test.expect(test.dut.at1.send_and_verify('AT^SLCC=1', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SLCC?', "\^SLCC: 1\s+OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SLCC=0', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SLCC?', "\^SLCC: 0\s+OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SLCC', exec_res))

        test.log.step('2. Test, Read, write and exec command with PIN')
        # If value is different for products, should be configured in local.cfg or dstl
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=?", test_res))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC?", "\^SLCC: 0\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC", exec_res))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC?", "\^SLCC: 1\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\^SLCC: 1"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=0", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC?", "\^SLCC: 0\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\^SLCC: 0"))

        test.log.step('3. Save and restore settings: AT&W, AT&F')
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC?", "\^SLCC: 1\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT^SLCC?", "\^SLCC: 0\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\^SLCC: 0"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify(f"AT^SLCC?", "\^SLCC: 0\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT^SLCC?", "\^SLCC: 1\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\^SLCC: 1"))

        test.log.step('4. Invalid parameters')
        invalid_error = "\+CME ERROR: invalid index"
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=-1", invalid_error))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=2", invalid_error))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1a", invalid_error))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=", invalid_error))

        test.log.step('5. Functionality test')
        test.log.step('5.1 Incoming voice call - SLCC: 0')
        r1_nat_number = test.r1.sim.nat_voice_nr
        r1_number_regexpr = r1_nat_number
        if r1_number_regexpr.startswith('0'):
            r1_number_regexpr = '.*' + r1_number_regexpr[1:]

        test.expect(test.dut.at1.send_and_verify("AT+CRC=0", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=0", "OK"))
        test.delete_all_entries_from_pb()
        test.r1.at1.send(f"ATD{test.dut.sim.int_voice_nr};")
        test.expect(test.dut.at1.wait_for("RING"))
        slcc_before_answer = f'\^SLCC: 1,1,4,0,0,0,"{r1_number_regexpr}",(129|145)\s+OK'
        test.expect(test.dut.at1.send_and_verify("AT^SLCC", slcc_before_answer))
        test.expect(test.dut.at1.send_and_verify("ATA", "OK"))
        slcc_after_answer = f'\^SLCC: 1,1,0,0,0,0,"{r1_number_regexpr}",(129|145)\s+OK'
        test.expect(test.dut.at1.send_and_verify("AT^SLCC", slcc_after_answer))
        if test.cpas_check:
            test.expect(test.dut.at1.send_and_verify("AT+CPAS?", "CPAS: 4\s+OK"))
        test.dut.at1.send("AT+CHUP")
        test.expect(test.r1.at1.wait_for("NO CARRIER"))

        test.log.step('5.2 Outgoing voice call - SLCC: 0')
        test.expect(test.dut.at1.send_and_verify("AT^SLCC?", "\^SLCC: 0\s+OK"))
        test.dut.at1.send(f"ATD{test.r1.sim.int_voice_nr};")
        test.expect(test.r1.at1.wait_for("RING"))
        test.expect(test.r1.at1.send_and_verify("ATA", "OK"))
        r1_int_number_regex = test.r1.sim.int_voice_nr.replace('+', '\+')
        slcc_response = f'\^SLCC: 1,0,0,0,0,0,"{r1_int_number_regex}",145\s+OK'
        # It may take some time until we get the correct result from AT^SLCC
        test.attempt(test.dut.at1.send_and_verify, "AT^SLCC", slcc_response, sleep=1, retry=5)
        if test.cpas_check:
            test.expect(test.dut.at1.send_and_verify("AT+CPAS?", "CPAS: 4\s+OK"))
        test.dut.at1.send("AT+CHUP")
        test.expect(test.r1.at1.wait_for("NO CARRIER"))

        test.log.step('5.3 Incoming voice call - SLCC: 1')
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.r1.at1.send(f"ATD{test.dut.sim.int_voice_nr};")
        slcc_before_answer = f'\^SLCC: 1,1,4,0,0,0,"{r1_number_regexpr}",(129|145)'
        test.expect(test.dut.at1.wait_for(slcc_before_answer))
        test.expect(test.dut.at1.wait_for("RING"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC", slcc_before_answer))
        test.expect(test.dut.at1.send_and_verify("ATA", "OK"))
        slcc_after_answer = f'\^SLCC: 1,1,0,0,0,0,"{r1_number_regexpr}",(129|145)'
        test.expect(test.dut.dstl_check_urc(slcc_after_answer))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC", slcc_after_answer))
        if test.cpas_check:
            test.expect(test.dut.at1.send_and_verify("AT+CPAS?", "CPAS: 4\s+OK"))
        test.dut.at1.send("AT+CHUP")
        test.expect(test.r1.at1.wait_for("NO CARRIER"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC", "AT\^SLCC\s+OK"))

        test.log.step('5.4 Outgoing voice call - SLCC: 1')
        test.expect(test.dut.at1.send_and_verify("AT^SLCC?", "\^SLCC: 1\s+OK"))
        slcc_before_answer = f'\^SLCC: 1,0,2,0,0,0,"{r1_int_number_regex}",145'
        test.dut.at1.send(f"ATD{test.r1.sim.int_voice_nr};")
        test.expect(test.dut.at1.wait_for(slcc_before_answer))
        test.expect(test.r1.at1.wait_for("RING"))
        test.expect(test.r1.at1.send_and_verify("ATA", "OK"))
        slcc_response = f'\^SLCC: 1,0,0,0,0,0,"{r1_int_number_regex}",145\s+OK'
        # It may take some time until we get the correct result from AT^SLCC
        test.attempt(test.dut.at1.send_and_verify, "AT^SLCC", slcc_response, retry=5, sleep=1)
        if test.cpas_check:
            test.expect(test.dut.at1.send_and_verify("AT+CPAS?", "CPAS: 4\s+OK"))
        test.dut.at1.send("AT+CHUP")
        test.expect(test.r1.at1.wait_for("NO CARRIER"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC", "AT\^SLCC\s+OK"))

        # Data Call: Not implemented since Viper does not support.
        pass

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        pass

    def delete_all_entries_from_pb(test):
        test.attempt(test.dut.at1.send_and_verify, "AT+CPBS?", "OK", sleep=1, retry=5)
        storage_text = re.findall('\+CPBS: "(\w+)",\d.*', test.dut.at1.last_response)
        if storage_text:
            storage = storage_text[0]
            test.expect(test.dut.dstl_clear_select_pb_storage(storage))
        pass


if "__main__" == __name__:
    unicorn.main()
