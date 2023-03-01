# responsible: matthias.reissner@thalesgroup.com
# location: Berlin
# TC0000001.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.devboard import devboard

class Test(BaseTest):
    """ Test example for devboard DSTL methods   """

    def setup(test):
        pass

    def run(test):

        # Disable local echo from ASC0 on devboard interface
        #test.expect(devboard.dstl_switch_off_at_echo(test.dut, 0))   # param 0 = ASC0, 1 would be ASC1
        #test.dut.at1.send_and_verify("ati")                          # please specify at1 to ASC0

        # Disable local echo from ASC0 on devboard interface
        #test.expect(devboard.dstl_switch_on_at_echo(test.dut))       # default is 0, ASC0
        #test.dut.at1.send_and_verify("ati")

        # Switch Antenna mode
        #test.expect(devboard.dstl_switch_antenna_mode_via_dev_board(test.dut, 1, "OFF"))
        #test.sleep(3)
        #test.expect(devboard.dstl_switch_antenna_mode_via_dev_board(test.dut, 1, "ON1"))
        
        # remove SIM
        #test.expect(devboard.dstl_remove_sim(test.dut))

        # insert SIM
        #test.expect(devboard.dstl_insert_sim(test.dut))

        # Check if module is on
        #test.expect(devboard.dstl_check_if_module_is_on_via_dev_board(test.dut))

        # Reset module via EMERGOFF
        #test.expect(devboard.dstl_reset_with_emergoff_via_dev_board(test.dut))

        # Reset module via VBATT
        #test.expect(devboard.dstl_reset_with_vbatt_via_dev_board(test.dut))

        # Switch OFF module USB
        #test.expect(devboard.dstl_turn_module_usb_off_via_dev_board(test.dut))

        # Switch ON module USB
        #test.expect(devboard.dstl_turn_module_usb_on_via_dev_board(test.dut))

        # Switch OFF devboard URC's
        #test.expect(devboard.dstl_turn_off_dev_board_urcs(test.dut))

        # Switch ON devboard URC's
        #test.expect(devboard.dstl_turn_on_dev_board_urcs(test.dut))

        # Switch antenna mode
        #test.expect(devboard.dstl_switch_antenna_mode_via_deb_board(test.dut, ant_nr = 1, mode = "OFF"))
        #test.expect(devboard.dstl_switch_antenna_mode_via_deb_board(test.dut, ant_nr = 1, mode = "ON1"))
        pass

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
