# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0091855.001


import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle


class Test(BaseTest):
    """
    TC0091855.001 - TpAtCrcBasic
    Intention: This procedure provides basic tests "for the test and write command of +CRC.
    Subscriber: 2
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())

        test.dut.at1.send_and_verify("AT+CPAS", "OK|ERROR")
        if 'OK' in test.dut.at1.last_response:
            test.cpas_check = True
        else:
            test.cpas_check = False
        pass

    def run(test):
        r1_nat_number = test.r1.sim.nat_voice_nr
        r1_num_regexpr = r1_nat_number
        if r1_num_regexpr.startswith('0'):
            r1_num_regexpr = '.*' + r1_num_regexpr[1:]
        elif r1_num_regexpr.startswith('+'):    # I saw an int.number in the log which did not worked without the lines!
            r1_num_regexpr = '.*' + r1_num_regexpr[3:]

        test.log.step('1. Test, Read, write and exec command without PIN')
        # Configuration need be added to local.cfg or dstl if AT+CRC is not pin protected for some products
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '\+CPIN: SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CRC=?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('AT+CRC?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('AT+CRC', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('AT+CRC=0', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('AT+CRC=1', '\+CME ERROR: SIM PIN required'))

        test.log.step('2. Test, Read, write and exec command with PIN')
        # If value is different for products, should be configured in local.cfg or dstl
        test_res = "\+CRC: \(0,1\)\s+OK"
        read_res = "\+CRC: [01]\s+OK"
        exec_res = "AT\+CRC\s+OK\s+"
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+CRC=?", test_res))
        test.expect(test.dut.at1.send_and_verify("AT+CRC?", read_res))
        test.expect(test.dut.at1.send_and_verify("AT+CRC", exec_res))
        test.expect(test.dut.at1.send_and_verify("AT+CRC=1", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CRC?", "\+CRC: 1\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+CRC: 1"))
        test.expect(test.dut.at1.send_and_verify("AT+CRC=0", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CRC?", "\+CRC: 0\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+CRC: 0"))

        test.log.step('3. Functionality test - Incoming voice call - CRC: 0')
        test.delete_all_entries_from_pb()
        test.r1.at1.send(f"ATD{test.dut.sim.int_voice_nr};")
        test.expect(test.dut.at1.wait_for("RING"))
        test.expect(test.dut.at1.send_and_verify("ATA", "OK"))
        clcc_response = f'\+CLCC: 1,1,0,0,0,"{r1_num_regexpr}",(129|145)\s+OK'
        for i in range(5):
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", clcc_response))
            if test.cpas_check:
                test.expect(test.dut.at1.send_and_verify("AT+CPAS", "CPAS: 4\s+OK"))
            test.sleep(0.5)

        test.dut.at1.send("AT+CHUP")
        test.expect(test.r1.at1.wait_for("NO CARRIER"))

        test.log.step('4. Functionality test - Incoming voice call - CRC: 1')
        test.expect(test.dut.at1.send_and_verify("AT+CRC=1", "OK"))
        test.r1.at1.send(f"ATD{test.dut.sim.int_voice_nr};")
        test.expect(test.dut.at1.wait_for("\+CRING: VOICE"))
        test.expect(test.dut.at1.send_and_verify("ATA", "OK"))
        # r1_nat_number = test.r1.sim.nat_voice_nr
        # r1_int_number = test.r1.sim.int_voice_nr.replace('+', '\+')
        clcc_response = f'\+CLCC: 1,1,0,0,0,"{r1_num_regexpr}",(129|145)\s+OK'
        for i in range(5):
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", clcc_response))
            if test.cpas_check:
                test.expect(test.dut.at1.send_and_verify("AT+CPAS", "CPAS: 4\s+OK"))
            test.sleep(0.5)

        test.dut.at1.send("AT+CHUP")
        test.expect(test.r1.at1.wait_for("NO CARRIER"))

        test.log.step('5. Invalid parameters')
        invalid_error = "+CME ERROR: invalid index"
        test.expect(test.dut.at1.send_and_verify("AT+CRC=-1", invalid_error))
        test.expect(test.dut.at1.send_and_verify("AT+CRC=2", invalid_error))
        test.expect(test.dut.at1.send_and_verify("AT+CRC=1a", invalid_error))
        test.expect(test.dut.at1.send_and_verify("AT+CRC=", invalid_error))

        test.log.step('5. Save and restore settings')
        test.expect(test.dut.at1.send_and_verify("AT+CRC?", "\+CRC: 1\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+CRC: 1"))
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CRC?", "\+CRC: 0\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+CRC: 0"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        if test.dut.project is 'VIPER':  # VPR02-941: SIM BUSY expected - not to fix
            test.attempt(test.dut.at1.send_and_verify, f"AT+CRC?", "\+CRC: 0\s+OK", retry=5, sleep=1)
        else:
            test.expect(test.dut.at1.send_and_verify(f"AT+CRC?", "\+CRC: 0\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CRC=1", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        if test.dut.project is 'VIPER':  # VPR02-941: SIM BUSY expected - not to fix
            test.attempt(test.dut.at1.send_and_verify, f"AT+CRC?", "\+CRC: 1\s+OK", retry=5, sleep=1)
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CRC?", "\+CRC: 1\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+CRC: 1"))
        pass

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        pass

    def delete_all_entries_from_pb(test):
        test.dut.at1.send_and_verify("AT+CPBS?")
        storage_text = re.findall('\+CPBS: "(\w+)",\d.*', test.dut.at1.last_response)
        if storage_text:
            storage = storage_text[0]
            test.expect(test.dut.dstl_clear_select_pb_storage(storage))
        pass


if "__main__" == __name__:
    unicorn.main()
