#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0092516.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.serial_interface import config_baudrate
import time

class Test(BaseTest):
    """
    TC0092516.001 IprSetting
    Checking functionality of all supported bitrates.
    responsible: agata.mastalska@globallogic.com
    location: Wroclaw
    """
    original_baudrate_str = ''
    dut_at1_original_settings = None

    def setup(test):
        # save original settings from device.cfg as stated in IPIS100333554
        test.dut_at1_original_settings = dict(test.dut.at1.settings)

        # check if we can find a running baudrate - if already misconfigured
        test.dut.dstl_find_current_baudrate([], test.dut.at1)
        test.dut.dstl_detect()

        test.original_baudrate_str = test.expect(test.dut.dstl_get_baudrate(test.dut.at1))


    def run(test):
        test.log.step("1.Check supported bitrates AT+IPR=?")
        supported_baudrates = test.dut.dstl_get_supported_baudrate_list()
        previous_baudrate = test.original_baudrate_str
        if test.original_baudrate_str not in supported_baudrates:
            test.log.error("##> current baudrate in module is NOT found in supported baudrates list, we set back to original value from device.cfg!")
            test.dut.at1.reconfigure(test.dut_at1_original_settings)
            test.expect(False, critical=True)
            return

        for bitrate in supported_baudrates:
#           IN CASE your place also does not suppot the highest BR, use this:
#            if bitrate == '921600':
#                test.log.step("bitrate {} not supported of my test place, we ignore it ".format(bitrate))
#                continue

            test.log.step("bitrate {} | 2. Set supported bitrate on module. \
                (starting from the lowest value)".format(bitrate))
            ret = test.dut.dstl_set_baudrate(bitrate, test.dut.at1)
            if not ret:
                test.log.step("failed to set bitrate {}, lets check which one is working now! ".format(bitrate))
                ret = test.expect(test.dut.at1.send_and_verify('AT', 'OK'))
                if not ret:
                    test.log.step("current bitrate {} does not work, lets try previous one! ".format(bitrate))
                    test.dut.at1.reconfigure(settings={"baudrate": previous_baudrate})
                    time.sleep(2)
                    ret = test.expect(test.dut.at1.send_and_verify('AT', 'OK'))
                    if not ret:
                        test.log.step(
                            "previous bitrate {} also does not work, unclear which baudrate may work, let's try all known baudrates:".format(previous_baudrate))
                        ret = test.dut.dstl_find_current_baudrate([], test.dut.at1)
                        if not ret:
                            test.log.step("no legal baudrate is working - check manually - ABORT! set back to original value from device.cfg!")
                            test.dut.at1.reconfigure(test.dut_at1_original_settings)
                            test.expect(False, critical=True)
                            return
                        else:
                            test.log.step("a working baudrate was found, overjumping baudrate under test! ")
                            continue
                    else:
                        test.log.step(
                            "previous bitrate {} works again, overjumping baudrate under test! ".format(previous_baudrate))
                        continue

                else:
                    test.log.step("current bitrate {} works, instead of problem in dstl_set_baudrate(), let's go on! ".format(bitrate))

            test.log.step("bitrate {} | 3. Send some AT commands e.g. AT, ATI.".format(bitrate))
            test.expect(test.dut.at1.send_and_verify('AT', 'OK'))
            test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))
            test.log.step("bitrate {} | 4. Restart module and check current bitrate.".format(bitrate))
            test.expect(test.dut.dstl_restart())
            test.expect(test.dut.dstl_get_baudrate(test.dut.at1) == bitrate)
            test.log.step("bitrate {} | 5. Repeat steps 3-4 increasing bitrate value according \
                 with documentation and finish on the highest value.".format(bitrate))

    def cleanup(test):
        baudrate_from_config = test.dut_at1_original_settings['baudrate']
        test.log.step('6. Set back to original baudrate AT+IPR={}.'.format(baudrate_from_config))
        test.expect(test.dut.dstl_set_baudrate(baudrate_from_config, test.dut.at1))


if "__main__" == __name__:
    unicorn.main()
