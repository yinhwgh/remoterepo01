#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0104651.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei


class Test(BaseTest):
    """
    Check basic functionality of ADC.

    1. Send test command AT^SRADC=?
    2. Send AT^SRADC?
    3. For all possible channels make single measurement by AT^SRADC=channel
    4. For all possible channels make periodic measurement:
    4a) Open measurement by AT^SRADC=channel,1,time. Use all basic time values from AT SPEC.
    4b) Close measurement by AT^SRADC=channel,0
    5. Try to use some wrong parameters of channel, operation and time.
    """

    def setup(test):
        test.BASIC_TIME_PERIODS = [100, 200, 250, 500, 1000, 30000]
        test.WRONG_TIME_PERIODS = [-100, -1, 1, 99, 30001, 300000]
        test.AVAILABLE_CHANNELS = [0]
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step("1. Send test command AT^SRADC=?")
        test.expect(test.dut.at1.send_and_verify("AT^SRADC=?", ".*SRADC: (\\d),\\((\\d.*)\\),\\((\\d.*)\\).*", wait_for="OK"))

        test.log.step("2. Send AT^SRADC?")
        test.expect(test.dut.at1.send_and_verify("AT^SRADC?", ".*SRADC: \\d,\\d*,\\d.*", wait_for="OK"))

        test.log.step("3. For all possible channels make single measurement by AT^SRADC=channel")
        for channel in test.AVAILABLE_CHANNELS:
            test.expect(test.dut.at1.send_and_verify("AT^SRADC={}".format(channel), ".*SRADC: {},1,\\d.*".format(channel), wait_for="OK"))

        test.log.step("4. For all possible channels make periodic measurement:")
        for channel in test.AVAILABLE_CHANNELS:
            for time_period in test.BASIC_TIME_PERIODS:
                test.log.step("4a) Open measurement by AT^SRADC=channel,1,time. Use all basic time values from AT SPEC.")
                test.expect(test.dut.at1.send_and_verify("AT^SRADC={0},1,{1}".format(channel, time_period), ".*OK.*"))
                test.expect(test.dut.at1.wait_for(".*SRADC: \\d,\\d*,\\d.*", timeout=30))

                test.log.step("4b) Close measurement by AT^SRADC=channel,0")
                test.expect(test.dut.at1.send_and_verify("AT^SRADC={},0".format(channel), ".*OK.*"))

        test.log.step("5. Try to use some wrong parameters of channel, operation and time.")
        test.expect(test.dut.at1.send_and_verify("AT^SRADC=21,1,100", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SRADC=0,5,100", ".*ERROR.*"))

        for wrong_time_period in test.WRONG_TIME_PERIODS:
            test.expect(test.dut.at1.send_and_verify("AT^SRADC=0,1,{}".format(wrong_time_period), ".*ERROR.*"))

    def cleanup(test):
        for channel in test.AVAILABLE_CHANNELS:
            test.expect(test.dut.at1.send_and_verify("AT^SRADC={},0".format(channel), ".*OK.*"))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
