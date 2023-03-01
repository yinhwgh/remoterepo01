# responsible: yuan.gao@thalesgroup.com
# author: christoph.dehm@thalesgroup.com
# location: Dalian, Berlin
# TC0104469.001
#

""" description:

    Check FD-Lock for USSD-, *#- commands and emergency calls
    1. check USSD action if they work generally
    2. Lock FD
    3. try some voice calls to check if lock is working
    4. ALL USSD actions should be prohibited now
    5. ALL EM-CALLs should work
    6. ALL *  # -sequences should be prohibited
    7. write USSD string to FD-PB
    8. lock FD-PB again
    9. only one USSD action should work, the other should not
    10. all emergency calls should work
    11. only one  *# -sequence should work, others are prohibited

    Taken from old MIT-STP: fd_lock_other_all_01.stp
    wm1: DUT_ASC0
"""

import unicorn
from core.basetest import BaseTest
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.configuration import shutdown_smso
from dstl.auxiliary.devboard import devboard
from dstl.auxiliary import init


class Test(BaseTest):
    """
    test description of TC0104469.001 ShutdownURCCrossCheck:
        1.Set at^scfg="URC/Ringline","asc0" and "URC/Ringline/ActiveTime","2"
        2.at^smso,wait pop up SHUTDOWN
        3.Check the ringline light
        4.In hight/low temperature,check whether pop up shutdown urc
        5.When voltage is hightest/lowest,check whether pop up shutdown urc

    this TS verifies with Serval only the appearance of the RING0 activity - not the period length
    As the expected result says: 3.Ringline is on.(Note for Serval: Ringlie will not be toggled by SHUTDOWN URC)

    - temperature topics are not handled here due to be able to run automatically
    - overvoltage SHUTDOWN is also not possible, McTest allows only 4.5V, whilst Serval reaches 4.8V

    -> please check situation for other products in detail!

    """

    def setup(test):
        test.tln_dut_nat = test.dut.sim.nat_voice_nr

        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        # test.dut.dstl_enter_pin()

        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2", ".*OK.*"))

        if 'asc_0' in test.dut.at1.name:
            test.log.info(' ASC0 found on at1')
            test.device_interface = 'at1'
        elif 'asc_0' in test.dut.at2.name:
            test.log.info(' ASC0 found on at2')
            test.device_interface = 'at2'
        elif 'asc_0' in test.dut.at3.name:
            test.log.info(' ASC0 found on at3')
            test.device_interface = 'at3'
        elif 'asc_0' in test.dut.at4.name:
            test.log.info(' ASC0 found on at4')
            test.device_interface = 'at4'
        else:
            test.expect(False, critical=True, msg="no dut-port for ASC0 found: abort! - check manually!")

        test.dut.dstl_turn_on_dev_board_urcs()
        pass

    def run(test):
        test.log.step(' 1. check and set SCFG=URC/Ringline ')
        device_interface = eval("test.dut." + test.device_interface)
        test.expect(device_interface.send_and_verify('AT^SCFG=URC/Ringline', '.*OK.*'))
        test.expect(device_interface.send_and_verify('AT^SCFG=URC/Ringline/ActiveTime', '.*OK.*'))

        test.expect(device_interface.send_and_verify('AT^SCFG=URC/Ringline,asc0', '.*OK.*'))
        test.expect(device_interface.send_and_verify('AT^SCFG=URC/Ringline/ActiveTime,2', '.*OK.*'))

        # _________________________________________________________
        test.log.step(' 2. shutdown by AT^SMSO')
        resp_devboard = test.dut.devboard.last_response  # clear buffer
        test.dut.devboard.send_and_verify('MC:Timeinfo=ON')
        test.dut.dstl_shutdown_smso(test.device_interface)
        test.sleep(8)
        test.dut.devboard.send_and_verify('MC:Timeinfo=OFF')
        resp_devboard = test.dut.devboard.last_response  # get URCs with RINGline: *  and time stamps
        print(resp_devboard)
        test._check_ring_period(resp_devboard)
        if '^SHUTDOWN' in device_interface.last_response:
            test.expect(True, msg=" URC ^SHUTDOWN found on ASC0")
        else:
            test.expect(False, msg="URC ^SHUTDDOWN not found on ASC0")

        # wakeup
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT'))

        # _________________________________________________________
        test.log.step(' 3. URC only for UNDERVOLTAGE warning')
        resp_devboard = test.dut.devboard.last_response  # clear buffer
        test.dut.devboard.send_and_verify('MC:Timeinfo=ON')
        test.dut.devboard.send_and_verify('MC:VBATT=2700')

        test.sleep(8)
        test.dut.devboard.send_and_verify('MC:Timeinfo=OFF')
        resp_devboard = test.dut.devboard.last_response  # get URCs with RINGline: *  and time stamps
        test.dut.devboard.send_and_verify('MC:VBATT=4100')
        print(resp_devboard)
        test._check_ring_period(resp_devboard)
        # wakeup
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT'))

        # _________________________________________________________
        test.log.step(' 4. shutdown by UNDERVOLTAGE')
        resp_devboard = test.dut.devboard.last_response  # clear buffer
        test.dut.devboard.send_and_verify('MC:Timeinfo=ON')
        test.dut.devboard.send_and_verify('MC:VBATT=2500')

        test.sleep(8)
        test.dut.devboard.send_and_verify('MC:Timeinfo=OFF')
        resp_devboard = test.dut.devboard.last_response  # get URCs with RINGline: *  and time stamps
        test.dut.devboard.send_and_verify('MC:VBATT=4100')
        print(resp_devboard)
        test._check_ring_period(resp_devboard)
        # wakeup
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT'))

        # wakeup
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT'))

        print("end of run")
        pass

    def cleanup(test):
        test.log.info(' *** Test End, clean up *** ')
        test.expect(test.dut.at1.send_and_verify('ATi'))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=URC/Ringline,local", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=URC/Ringline/ActiveTime,2", ".*OK.*"))
        test.dut.devboard.send_and_verify('MC:Timeinfo=OFF')
        """
        test.dut.dstl_lock_unlock_facility(facility='FD', lock=False)
        # delete phonebook FD
        test.dut.dstl_clear_select_pb_storage('FD')
        # change to SM phonebook
        test.dut.dstl_set_pb_memory_storage('SM')
        test.dut.at1.send_and_verify('at+CCWA=0')
        test.dut.at1.send_and_verify('at+CUSD=0')
        """
        pass

    def _check_ring_period(test, resp):
        if test.dut.project in 'SERVAL':
            if 'RINGline: 0' in resp:
                test.log.info(' RINGline action found')
                return True
            else:
                test.expect(False, msg=" RINGline action not found")
        else:
            test.expect(False, msg=" _check_ring_periode(): not prepared for project {}".format(test.dut.project))
        return False


if "__main__" == __name__:
    unicorn.main()
