# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0091903.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.status_control.configure_event_reporting import dstl_configure_common_event_reporting
import dstl.sms.send_sms_message
# deprecated: from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.auxiliary.devboard.devboard import dstl_switch_off_at_echo, dstl_switch_on_at_echo, \
    dstl_turn_on_dev_board_urcs, dstl_turn_off_dev_board_urcs
from dstl.call import setup_voice_call
from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_close_file, dstl_remove_file


class Test(BaseTest):
    """
    TC0091903.001 - TpAtSindVmWait
    Check the status for indicator vmwait(1/2)
    Currently this is supported only in the Berlin testnetwork.
    Mario has installed a specific device which receives incoming command SMS or URLs and triggers
    to send VM wait messages to some specific subscribers.
    For details see:
    https://confluence.gemalto.com/pages/viewpage.action?spaceKey=IWIKI&title=Testnetz
    section: "VMwait messages:"
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_switch_off_at_echo()
        test.dut.dstl_switch_off_at_echo(serial_ifc=1)
        test.dut.dstl_turn_on_dev_board_urcs()
        test.expect(test.dut.dstl_enter_pin())
        # Set module with pin locked
        # test.expect(test.dut.dstl_lock_sim())
        # test.expect(test.dut.dstl_lock_sim())
        pass

    def run(test):
        # nat_dut_phone_num = test.dut.sim.nat_voice_nr
        nat_r1_phone_num = test.r1.sim.nat_voice_nr

        test.log.step('1.1 Test (basic functionalities)')
        test.dut.at1.send_and_verify("at^sind=service,0")
        test.dut.at1.send_and_verify("at^sind=message,1")
        test.dut.at1.send_and_verify("at^sind=call,0")
        test.dut.at1.send_and_verify("at^sind=roam,0")
        test.dut.at1.send_and_verify("at^sind=smsfull,0")
        test.dut.at1.send_and_verify("at^sind=rssi,0")

        test.dut.at1.send_and_verify("at^sind=ciphcall,0")
        test.dut.at1.send_and_verify("at^sind=eons,0")
        test.dut.at1.send_and_verify("at^sind=nitz,0")

        test.dut.at1.send_and_verify("at^sind=battchg,0")
        test.dut.at1.send_and_verify("at^sind=signal,0")
        test.dut.at1.send_and_verify("at^sind=sounder,0")
        test.dut.at1.send_and_verify("at^sind=audio,0")
        test.dut.at1.send_and_verify("at^sind=vmwait1,0")
        test.dut.at1.send_and_verify("at^sind=vmwait2,0")

        test.dut.dstl_configure_common_event_reporting(1, 0, 0, 2)
        test.dut.at2.send_and_verify('at^sind=vmwait1,2')

        #   ********************************************************************
        #    1.2 Test vmwait1 indicator with a single voice mail notification
        #        disable vmwait1 indicator and sent a voice mail notification
        #        vmwait URC should not be displayed on C1!
        #   ********************************************************************
        test.log.step('1.2 Test disabled vmwait1 indicator with a single voice mail notification)')
        test.dut.at1.send_and_verify("at^sind?")
        test.generate_vm_notification(test.dut.sim.nat_voice_nr, True)
        test.wait(27)
        buf = test.dut.at1.last_response
        if 'CIEV:' in buf:
            test.expect(False, msg="URC +CIEV: appeared - not expected at this step")
        test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,0,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", '\^SIND: vmwait1,0,1.*\^SIND: vmwait2,0,0.*OK.*'))

        test.generate_vm_notification(test.dut.sim.nat_voice_nr, False)
        buf = test.dut.at1.last_response
        if 'CIEV:' in buf:
            test.expect(False, msg="URC +CIEV: appeared - not expected at this step")
        test.dut.at1.send_and_verify("at^sind=vmwait1,2")
        test.wait(17)   # wait to reveice the message from network
        test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", '\^SIND: vmwait1,0,0.*\^SIND: vmwait2,0,0.*OK.*'))
        test.wait(7)
        test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,0,0.*OK.*'))

        #    ********************************************************************
        #     1.3 Test vmwait1 indicator with a single voice mail notification
        #         enable vmwait1 indicator and sent a voice mail notification
        #         vmwait URC should be displayed on C1!
        #    ********************************************************************
        test.log.step('1.3 Test enabled vmwait1 indicator with a single voice mail notification)')
        test.dut.at1.send_and_verify("at^sind=vmwait1,1")
        test.dut.at1.send_and_verify("at^sind=vmwait2,1")
        test.dut.at1.send_and_verify("at^sind?")
        test.generate_vm_notification(test.dut.sim.nat_voice_nr, True)
        test.expect(test.dut.at1.wait_for("\+CIEV: vmwait1,1", timeout=40))
        test.wait(7)
        test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,1,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", '\^SIND: vmwait1,1,1.*\^SIND: vmwait2,1,0.*OK.*'))

        test.generate_vm_notification(test.dut.sim.nat_voice_nr, False)
        test.expect(test.dut.at1.wait_for("\+CIEV: vmwait1,0", timeout=40))
        test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,1,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", '\^SIND: vmwait1,1,0.*\^SIND: vmwait2,1,0.*OK.*'))
        test.wait(7)
        test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,1,0.*OK.*'))

        #   ************************************************************************************
        #    2. Test vmwait1 indicator with three voice mail notifications during a voice call
        #        enable vmwait1 indicator and sent voice mail notifications
        #        vmwait URC should be displayed on C1!
        #    ************************************************************************************
        test.log.step('2) Test vmwait1 indicator with three voice mail notifications during a voice call')
        test.dut.at1.send_and_verify("at^sind=vmwait1,1")
        test.dut.at1.send_and_verify("at^sind=vmwait2,1")
        # test.dut.dstl_setup_and_maintain_call(test.r1, duration=1, direction=0)
        res = test.dut.dstl_voice_call_by_number(test.r1, nat_r1_phone_num)
        if res:
            print('helolo')
            test.generate_vm_notification(test.dut.sim.nat_voice_nr, True)
            test.expect(test.dut.at1.wait_for("\+CIEV: vmwait1,1", timeout=40))
            test.wait(7)
            test.generate_vm_notification(test.dut.sim.nat_voice_nr, True)
            test.expect(test.dut.at1.wait_for("\+CIEV: vmwait1,1", timeout=40))
            test.wait(7)
            test.generate_vm_notification(test.dut.sim.nat_voice_nr, True)
            test.expect(test.dut.at1.wait_for("\+CIEV: vmwait1,1", timeout=40))
            test.wait(7)
            test.expect(test.dut.at1.send_and_verify("at^sind?", '\^SIND: vmwait1,1,1.*\^SIND: vmwait2,1,0.*OK.*'))
            test.generate_vm_notification(test.dut.sim.nat_voice_nr, False)
            test.expect(test.dut.at1.wait_for("\+CIEV: vmwait1,0", timeout=40))
            test.wait(7)

        test.expect(test.dut.dstl_release_call())

        #   ************************************************************************************
        #    3. Test vmwait1 indicator while interface is in data mode - DISCARDING of CMER
        #        enable vmwait1 indicator, set CMER to 1 = discard and send vm-notifications
        #        One vmwait URC should be displayed after returning back to cmd mode on at1!
        #    ************************************************************************************
        test.log.step('3) vmwait1 ind. while in data mode - BUFFERING only 1 URC (+CMER=2)')
        test.dut.at1.send_and_verify("at^sind=vmwait1,1")
        test.dut.at1.send_and_verify("at^sind=vmwait2,1")
        test.dut.at2.send_and_verify('at^sind=vmwait1,2')
        test.dut.dstl_configure_common_event_reporting(1, 0, 0, 2)  # 1: discard URCs in data mode!
        test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,1,0.*OK.*'))
        test.dut.at1.send_and_verify("at^sfsa=?", '.*OK.*')
        if 'ERROR' in test.dut.at1.last_response:
            test.log.error(' AT^SFSA / flash file system seems not be available - overjumping this test step!')
        else:
            fh = test.dut.dstl_open_file('A:/test_vmwait.txt', 9)
            test.dut.at1.send(f"at^sfsa=write,{fh},5\r")
            test.dut.at1.wait_for("CONNECT", timeout=4)

            # interface is in cmd mode now, lets send some vmwaits. Interface should run in a timeout and return back
            test.generate_vm_notification(test.dut.sim.nat_voice_nr, True, device_interface="r1")
            test.sleep(7)
            test.dut.at1.send("B")      # send one character to trigger the timeout to zero
            test.dut.at2.send_and_verify('at^sind=vmwait1,2')
            test.generate_vm_notification(test.dut.sim.nat_voice_nr, False, device_interface="r1")
            # test.expect(test.dut.at1.wait_for("ERROR", timeout=140))
            test.expect(test.dut.at1.wait_for_strict("ERROR.*", timeout=140))
            test.sleep(15)
            buf = test.dut.at1.last_response
            if 'CIEV:' in buf:
                test.expect(False, msg="+CIEV URC found in response - should not appear: ERROR!")
            test.dut.dstl_close_file(fh)
            test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,1,0.*OK.*'))

            #   ************************************************************************************
            #    4. Test vmwait1 indicator while interface is in data mode - BUFFERING of CMER
            #       enable vmwait1 indicator, set CMER to 3=buffering and send vm-notifications
            #       Last vmwait URC should be displayed after returning back to cmd mode on at1!
            #    ************************************************************************************
            test.log.step('4) vmwait1 ind. while in data mode - BUFFERING more URCs (+CMER=3)')
            test.dut.at1.send_and_verify("at^sind=vmwait1,1")
            test.dut.at1.send_and_verify("at^sind=vmwait2,1")
            test.dut.at2.send_and_verify('at^sind=vmwait1,2')
            # test.dut.at2.send_and_verify('at+CPMS?')
            test.dut.dstl_turn_on_dev_board_urcs()
            test.dut.dstl_configure_common_event_reporting(3, 0, 0, 2)  # 3: buffer more URC!
            test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,1,0.*OK.*'))
            fh = test.dut.dstl_open_file('A:/test_vmwait.txt', 9)
            test.dut.at1.send(f"at^sfsa=write,{fh},5\r")
            test.dut.at1.wait_for("CONNECT", timeout=4)

            # interface is in cmd mode now, lets send some vmwaits. Interface should run in a timeout and return back
            test.generate_vm_notification(test.dut.sim.nat_voice_nr, True, device_interface="r1")
            test.sleep(15)
            test.dut.at1.send("B")      # send one character to trigger the timeout to zero
            test.dut.at2.send_and_verify('at^sind=vmwait1,2')
            test.dut.at2.send_and_verify('at+CPMS?')
            test.generate_vm_notification(test.dut.sim.nat_voice_nr, False, device_interface="r1")
            test.expect(test.dut.at1.wait_for_strict("ERROR.*\+CIEV: vmwait1,0", timeout=140))
            test.dut.dstl_close_file(fh)
            test.expect(test.dut.at1.send_and_verify("at^sind=vmwait1,2", '\^SIND: vmwait1,1,0.*OK.*'))
            test.dut.at2.send_and_verify('at+CPMS?')
        pass

    def cleanup(test):
        test.dut.dstl_turn_off_dev_board_urcs()
        test.dut.dstl_release_call()
        test.dut.dstl_close_file(0)
        test.dut.dstl_remove_file("A:/test_vmwait.txt")
        test.dut.at1.send_and_verify("at^sind=vmwait1,0")
        test.dut.at1.send_and_verify("at^sind=vmwait2,0")
        test.dut.dstl_configure_common_event_reporting(0, 0, 0, 0)
        test.generate_vm_notification(test.dut.sim.nat_voice_nr, False)
        test.dut.dstl_switch_on_at_echo()
        test.dut.dstl_switch_on_at_echo(serial_ifc=1)
        pass

    def generate_vm_notification(test, nat_number, set_state, device_interface="dut"):
        device_interface = eval("test." + device_interface)
        if set_state:
            msg = "sendvmn " + nat_number[-4:]
        else:
            msg = "deletevmn " + nat_number[-4:]

        msg_sent = device_interface.dstl_send_sms_message("+491723402085", msg, exp_resp='CMGS: .*OK.*')
        # ret = test.dut.at1.wait_for_strict("CMGS: ", timeout=4)
        if not msg_sent:
            print(device_interface.last_response)
            return False
        else:
            return True
        # return test.dut.at1.wait_for(r"\+CMGS: ", timeout=40)


if "__main__" == __name__:
    unicorn.main()
