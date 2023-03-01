#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105211.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.gpio.gpio_on_module import get_available_gpio_pins
from dstl.gpio.gpio_on_module import open_gpio_driver,close_gpio_driver,open_gpio_pin_as_input,open_gpio_pin_as_output_default,close_gpio_pin
import re

class Test(BaseTest):
    '''
    TC0105211.002 - VoiceWithGpioPinsConfiguration
    Intention:Test procedure to check the error handling and the functionality of the command AT^SCPIN.
    Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.set_all_to_gpio()
        test.dut.dstl_register_to_network()

    def run(test):
        test.log.step('0. Before the test, a voice call should be set up.')
        nat_r1_phone_num = test.r1.sim.nat_voice_nr
        test.dut.dstl_voice_call_by_number(test.r1, nat_r1_phone_num)

        test.log.step('1. Check the default output of at^scpin=? command')
        test.expect(test.dut.at1.send_and_verify('at^scpin=?', 'OK'))
        gpio_pin_list = test.dut.dstl_get_available_gpio_pins()
        print(gpio_pin_list)
        test_pin=gpio_pin_list[0]
        test.log.step('2. Open GPIO driver')
        test.dut.at1.send_and_verify('AT^SPIO=0', 'O')
        test.expect(test.dut.dstl_open_gpio_driver())

        test.log.step('3. Test with incorrect arguments of at^scpin:')
        test.log.step('3.1. Try to set incorrect mode parameter')
        test.expect(test.dut.at1.send_and_verify('at^scpin=3,0,0', 'ERROR'))
        test.log.step('3.2. Try to set incorrect pin_id parameter')
        test.expect(test.dut.at1.send_and_verify('at^scpin=1,30,0', 'ERROR'))
        test.log.step('3.3. Try to set incorrect direction parameter')
        test.expect(test.dut.at1.send_and_verify('at^scpin=1,0,3', 'ERROR'))
        test.log.step('3.4. Try to set incorrect startValue parameter')
        test.expect(test.dut.at1.send_and_verify('at^scpin=1,0,1,3', 'ERROR'))
        test.log.step('3.5. Try to set only mode parameter')
        test.expect(test.dut.at1.send_and_verify('at^scpin=1', 'ERROR'))
        test.log.step('3.6. Try to set only mode and pin_id parameter')
        test.expect(test.dut.at1.send_and_verify('at^scpin=1,1', 'ERROR'))

        test.log.step('4. Try to open again already opened pin')
        test.expect(test.dut.at1.send_and_verify(f'at^scpin=1,{test_pin},0', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'at^scpin=1,{test_pin},0', 'ERROR'))
        test.log.step('5. Try to close again already closed pin')
        test.expect(test.dut.at1.send_and_verify(f'at^scpin=0,{test_pin},0', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'at^scpin=0,{test_pin},0', 'ERROR'))
        test.log.step('6. Try to set pin as input while is already set as output')
        test.expect(test.dut.dstl_open_gpio_pin_as_output_default(test_pin))
        test.expect(test.dut.dstl_open_gpio_pin_as_input(test_pin)==False)
        test.log.step('7. Try to set pin as output while is already set as input')
        test.expect(test.dut.dstl_close_gpio_pin(test_pin))
        test.expect(test.dut.dstl_open_gpio_pin_as_input(test_pin))
        test.expect(test.dut.dstl_open_gpio_pin_as_output_default(test_pin)==False)
        test.expect(test.dut.dstl_close_gpio_pin(test_pin))
        test.log.step('8. Test with correct arguments of at^scpin:')
        test.log.step('8.1. Open all pins as output')
        for pin in gpio_pin_list:
            pin_index = pin - 1
            test.expect(test.dut.dstl_open_gpio_pin_as_output_default(pin_index))
        test.log.step('8.2. Close all pins')
        for pin in gpio_pin_list:
            pin_index =pin-1
            test.expect(test.dut.dstl_close_gpio_pin(pin_index))
        test.log.step('8.3. Open all pins as input')
        for pin in gpio_pin_list:
            pin_index = pin - 1
            test.expect(test.dut.dstl_open_gpio_pin_as_input(pin_index))
        test.log.step('8.4. Close all pins')
        for pin in gpio_pin_list:
            pin_index = pin - 1
            test.expect(test.dut.dstl_close_gpio_pin(pin_index))
        test.log.step('9. Close GPIO driver')
        test.expect(test.dut.dstl_close_gpio_driver())
        test.log.step('10. Check call status is still active, then release call')
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc())
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())

    def cleanup(test):
        test.log.info('***Test End***')

    def set_all_to_gpio(test):
        test.dut.at1.send_and_verify('at^scfg=?', 'OK')
        res = test.dut.at1.last_response
        pattern_1='\^SCFG: "GPIO/Mode/(\w+)",.*"gpio".*'
        support_line = re.findall(pattern_1, res)
        for line in support_line:
            test.expect(test.dut.at1.send_and_verify(f'at^scfg="GPIO/Mode/{line}","gpio"', 'OK'))
        test.dut.dstl_restart()


if "__main__" == __name__:
    unicorn.main()

