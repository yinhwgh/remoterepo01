# responsible: mariusz.wojcik@globallogic.com
# responsible: michal.jastrzebski@globallogic.com
#responsible: xiaoyu.chen@thalesgroup.com
# location: Wroclaw
# TC0103478.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary.devboard import sync_on_devboard
from dstl.network_service import register_to_network
from dstl.configuration import check_sync_status_for_sled
from dstl.security import set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    Check if possible to turn ON and OFF function: Status and Mode Indication via SYNC Line.

    1. Set AT^SLED=0
    2. Using McTest check, if SYNC line is off (MC:SYNC)
    3. Set AT^SLED=1
    4. Using McTest check, if SYNC line is on (MC:SYNC)
    5. Set AT^SLED=2
    6. Using McTest check, if SYNC line is blinking (MC:SYNC)
    7. Turn off SYNC line by AT^SLED=0
    8. Using McTest check, if SYNC line is off (MC:SYNC)
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step("1. Set AT^SLED=0.")
        test.expect(test.dut.dstl_set_sled_mode(0))

        test.log.step("2. Using McTest check, if SYNC line is off (MC:SYNC).")
        test.expect(test.dut.dstl_check_sync_status_for_sled(sled='0'))

        test.log.step("3. Set AT^SLED=1.")
        test.expect(test.dut.dstl_set_sled_mode(1))
        test.sleep(10)

        test.log.step("4. Using McTest check, if SYNC line is on (MC:SYNC).")
        test.expect(test.dut.dstl_check_sync_status_for_sled(sled='1'))

        test.log.step("5. Set AT^SLED=2.")
        test.expect(test.dut.dstl_set_sled_mode(2))

        test.log.step("6. Using McTest check, if SYNC line is blinking (MC:SYNC).")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.dstl_check_sync_status_for_sled(sled='2'))
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.dstl_check_sync_status_for_sled(sled='2', registered=True, data_transfer=False))

        test.log.step("7. Turn off SYNC line by AT^SLED=0.")
        test.expect(test.dut.dstl_set_sled_mode(0))

        test.log.step("8. Using McTest check, if SYNC line is off (MC:SYNC).")
        test.expect(test.dut.dstl_check_sync_status_for_sled(sled='0'))

    def cleanup(test):
        test.expect(test.dut.dstl_set_sled_mode(0))


if "__main__" == __name__:
    unicorn.main()
