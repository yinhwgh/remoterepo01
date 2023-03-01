#responsible: dan.liu@thalesgroup.com
#Dalian
#TC0103772.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary import check_urc
from dstl.auxiliary.devboard.devboard import DevboardInterface


class Test(BaseTest):
    """
    TC0103772.001 - VoltageRobustnessAgainsPowerSupplyLoss
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.devboard.send_and_verify('mc:urc=off', "OK")
        test.dut.devboard.send_and_verify('MC:URC=PWRIND', ".*OK.*")

    def run(test):

        test.log.step('4. Repeat 1-3 10 times')
        for i in range(1, 11):
            test.log.info('this is  {} loop'.format(i))
            test.power_off_on_dif_voltage(voltage=3400)
        test.log.step('5. Repeat 1-4 steps with 4.0v')
        for i in range(1, 11):
            test.log.info('this is  {} loop'.format(i))
            test.power_off_on_dif_voltage(voltage=4000)

    def cleanup(test):

        test.expect(test.dut.devboard.send_and_verify('MC:VBATT=3800', 'OK'))

    def power_off_on_dif_voltage(test, voltage):

        test.log.step('1.Set the power supply voltage {}v'.format(voltage))
        test.expect(test.dut.devboard.send_and_verify('MC:VBATT={}'.format(voltage), 'OK'))
        test.log.step('2.Keep the voltage 5 mins than switch off power supply')
        test.sleep(300)
        test.expect(test.dut.devboard.send_and_verify('MC:VBATT=off', '.*OK.*PWRIND: 1.*'))
        test.sleep(5)
        test.log.step('3. Power on module')
        test.expect(test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK'))
        test.expect(test.dut.devboard.send_and_verify('MC:igt=1000', '.*OK.*PWRIND: 0.*'))
        test.expect(test.dut.at1.wait_for("^SYSSTART", timeout=15))
        test.sleep(5)

if __name__ == "__main__":
    unicorn.main()
