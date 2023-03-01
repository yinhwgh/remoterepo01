#responsible: baris.kildi@thalesgroup.com
#location: Berlin
#TC0010783.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    def setup(test):
        test.expect(dstl_restart(test.dut))
        test.dut.dstl_detect()
        dstl_get_imei(test.dut)

    def run(test):

        test.log.step("1. Register module to network")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Force module into 2G")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=,,,0", ".*OK.*"))
        test.sleep(10)

        # Specify how many times module will call attach/detach GPRS
        test.loop = 50

        test.log.info("* check test command response")
        check_cgatt(test, 'test', 'OK')

        test.log.step("3. Start duration test of attach into network and detach from network " + str(test.loop) + " times")


        for i in range(test.loop):
            test.log.info("* read the actual setting - state should be 1")
            check_cgatt(test, 'read', 'OK', '1')

            test.log.info("* Detach from the network, set <state> to value ´0 in write command")
            check_cgatt(test, 'write', 'OK', '0')

            test.log.info("* read the actual setting - state should 0")
            check_cgatt(test, 'read', 'OK', '0')

            test.log.info("* Attach to the network, set <state> to value 1 in write command")
            check_cgatt(test, 'write', 'OK', '1')



    def cleanup(test):
        test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*")
        test.sleep(10)


def check_cgatt(test, mode, expected_response, value='0', invalid_read_command=False):
    if mode is 'test':
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=?", ".*\\+CGATT: \\(0[,-]1\\).*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=?", ".*{}.*".format(expected_response)))
    elif mode is 'write':
        test.expect(test.dut.at1.send_and_verify("AT+CGATT={}".format(value), ".*{}.*".format(expected_response)))
    elif mode is 'exec':
        test.expect(test.dut.at1.send_and_verify("AT+CGATT", ".*{}.*".format(expected_response)))
    else:
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGATT?", ".*\\+CGATT: {}.*OK.*".format(value)))
        else:
            if invalid_read_command:
                test.expect(test.dut.at1.send_and_verify("AT+CGATT?11?", ".*{}.*".format(expected_response)))
            else:
                test.expect(test.dut.at1.send_and_verify("AT+CGATT?", ".*{}.*".format(expected_response)))

if "__main__" == __name__:
    unicorn.main()
