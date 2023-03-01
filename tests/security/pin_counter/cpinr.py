#responsible: johann.suhr@thalesgroup.com
#location: Berlin
#TC0105034.001

import unicorn
from core.basetest import BaseTest

from dstl.internet_service import lwm2m_service
from dstl.auxiliary import init
from dstl.auxiliary import restart_module

import re
import random


def random_pin(type):
    if 'SIM PIN' in type:
        return random.randint(1000, 9999)
    elif 'SIM PUK' in type:
        return random.randint(10000000, 99999999)
    else:
        raise ValueError


class Test(BaseTest):
    """ Test at+cpinr command. """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.at1.send_and_verify(f'AT+CLCK="SC",1,"{test.dut.sim.pin1}"')
        test.dut.dstl_restart()
        pass

    def run(test):
        test.sleep(5)
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.dut.at1.send_and_verify("at+cpin?", "OK")
        cpinr_is_available = test.dut.at1.send_and_verify('AT+CPINR=?')
        test.expect(cpinr_is_available)

        _, initial_remaining_pin, max_pin = test.check_remaining_attempts('SIM PIN')

        if int(initial_remaining_pin) == 0:
            test.enter_code('SIM PUK', correct=True)
            _, initial_remaining_pin, max_pin = test.check_remaining_attempts('SIM PIN')

            test.dut.dstl_restart()

        # Enter wrong pin.
        test.sleep(5)
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.dut.at1.send_and_verify("at+cpin?", "OK")
        test.enter_code('SIM PIN', correct=False)

        # Check if remaining_pin has been decreased by 1.
        _, remaining_pin, max_pin = test.check_remaining_attempts('SIM PIN')

        test.expect(int(remaining_pin) == (int(initial_remaining_pin) - 1))

        # Enter correct pin.
        test.enter_code('SIM PIN', correct=True)

        # Check if remaining_pin has been increased by 1.
        _, remaining_pin, max_pin = test.check_remaining_attempts('SIM PIN')
        test.expect(int(remaining_pin) == int(initial_remaining_pin))

        test.dut.dstl_restart()

        # Check PUK
        test.sleep(5)
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.dut.at1.send_and_verify("at+cpin?", "OK")
        while int(remaining_pin) > 0:
            test.enter_code('SIM PIN', correct=False)
            _, remaining_pin, max_pin = test.check_remaining_attempts('SIM PIN')

        _, initial_remaining_puk, max_puk = test.check_remaining_attempts('SIM PUK')

        # Enter PUK wrong.
        test.enter_code('SIM PUK', correct=False)

        # Check if remaining_puk has been decreased by 1.
        _, remaining_puk, max_puk = test.check_remaining_attempts('SIM PUK')
        test.expect(int(remaining_puk) == int(initial_remaining_puk) - 1)

        # Enter PUK right.
        test.enter_code('SIM PUK', correct=True)

        # Check if remaining_puk has been increased by 1.
        _, remaining_puk, max_puk = test.check_remaining_attempts('SIM PUK')
        test.expect(int(remaining_puk) == int(initial_remaining_puk))

    def check_remaining_attempts(test, type):
        test.dut.at1.send_and_verify("at+cpin?", "OK")
        test.dut.at1.send_and_verify('AT+CPINR')
        last_resp = test.dut.at1.last_response

        pattern = fr'^\+CPINR.*{type}.*'
        pin_puk_info = re.search(pattern, last_resp, re.M).group()
        if pin_puk_info:
            type, counts, max_counts = pin_puk_info.split(',')
            return [type, counts, max_counts]
        else:
            return None

    def enter_code(test, type, correct):
        sim_pin = test.dut.sim.pin1
        sim_puk = test.dut.sim.puk1

        if 'SIM PIN' in type:
            if correct:
                test.dut.at1.send_and_verify(f'AT+CPIN="{sim_pin}"')
            else:
                sim_pin = random_pin('SIM PIN')
                test.dut.at1.send_and_verify(f'AT+CPIN="{sim_pin}"', '.*ERROR.*')
        elif 'SIM PUK' in type:
            if correct:
                test.dut.at1.send_and_verify(f'AT+CPIN="{sim_puk}","{sim_pin}"')
            else:
                sim_puk = random_pin('SIM PUK')
                test.dut.at1.send_and_verify(f'AT+CPIN="{sim_puk}","{sim_pin}"', '.*ERROR.*')
        else:
            return -1

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
