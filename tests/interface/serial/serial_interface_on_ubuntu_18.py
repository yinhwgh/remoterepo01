#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0104686.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
import dstl.network_service.register_to_network
import dstl.sms.sms_functions
import dstl.call.switch_to_command_mode


class Test(BaseTest):
    """
    Check Serial Interface ASC0 and ASC1 on Ubuntu 18.04.

    1. Connect module with PC with Ubuntu 18.04 via ASC0 interface.
    2. Check if module is present as ttySx (or ttyUSBx if using ADA adapter) device.
    3. Login to the network.
    4. Send Sms to remote.
    5. Check if remote has received SMS.
    6. Start PPP connection via ATD*99# and wait for "CONNECT".
    7. Stop PPP connection.
    Repeat steps 1-7 on ASC1 interface.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.r1.dstl_detect()
        test.r1.dstl_get_imei()
        test.r1.dstl_enable_sms_urc()

    def run(test):
        execute_steps(test, "ASC0", "ttyUSB0")

        test.log.step("Repeat steps 1-7 on ASC1 interface.")
        test.dut.at1 = test.dut.asc_1
        execute_steps(test, "ASC1", "ttyUSB1")

    def cleanup(test):
        test.dut.at1 = test.dut.asc_0
        test.dut.dstl_switch_to_command_mode_by_dtr()


def execute_steps(test, interface, linux_port):
    test.log.step("1. Connect module with PC with Ubuntu 18.04 via ASC0 interface.")
    test.log.info("Executing step on {} interface.".format(interface))
    test.expect("18.04" in test.os.execute('lsb_release -a'), critical=True)
    test.expect(test.dut.at1.send_and_verify('AT', '.*OK.*'))

    test.log.step("2. Check if module is present as ttySx (or ttyUSBx if using ADA adapter) device.")
    test.log.info("Executing step on {} interface.".format(interface))
    test.expect(linux_port in test.os.execute('ls /dev/'))

    test.log.step("3. Login to the network.")
    test.log.info("Executing step on {} interface.".format(interface))
    test.expect(test.dut.dstl_register_to_network())
    test.expect(test.r1.dstl_register_to_network())

    test.log.step("4. Send Sms to remote.")
    test.log.info("Executing step on {} interface.".format(interface))
    voice_number = test.r1.sim.int_voice_nr
    test.expect(test.dut.dstl_send_sms_message(voice_number, "Test SMS"))

    test.log.step("5. Check if remote has received SMS.")
    test.log.info("Executing step on {} interface.".format(interface))
    test.expect(test.r1.at1.wait_for("CMTI"))

    test.log.step("6. Start PPP connection via ATD*99# and wait for \"CONNECT\".")
    test.log.info("Executing step on {} interface.".format(interface))
    test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for='CONNECT'))

    test.log.step("7. Stop PPP connection.")
    test.log.info("Executing step on {} interface.".format(interface))
    test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())


if "__main__" == __name__:
    unicorn.main()
