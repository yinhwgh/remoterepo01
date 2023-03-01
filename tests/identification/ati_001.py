#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0000408.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_identification
from dstl.identification import check_identification_ati
from dstl.configuration import set_error_message_format

class TpAti(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("Checking all configured available ports.")
        test.ports = [test.dut.at1]
        if test.dut.at2 and test.dut.at2.send_and_verify("AT", ".*OK.*"):
            test.ports.append(test.dut.at2)
            test.log.info(f"Port {test.dut.at2.name} is available.")
        if test.dut.at3 and test.dut.at3.send_and_verify("AT", ".*OK.*"):
            test.ports.append(test.dut.at3)
            test.log.info(f"Port {test.dut.at3.name} is available.")
        test.ports_name = [port.name for port in test.ports]

    def run(test):
        test.log.info(f"***** Looping for ports {test.ports_name} *****")
        for test_port in test.ports:
            test.dut.dstl_restart()
            test.sleep(5)
            for pin_state in range(2):
                if pin_state == 0:
                    pin_locked = True
                    test.log.info('******* Tests under SIM PIN status *******')
                else:
                    pin_locked = False
                    test.dut.dstl_enter_pin()
                    test.log.info('******* Tests under SIM READY status *******')
                for i in range(1, 3):
                    test.log.info(f"***** Test for port {test_port.name}, AT+CMEE={i} *****")
                    test.log.step(f"{i}.1 OK response returns with valid commands - port {test_port.name}")
                    test.expect(test.dut.dstl_set_error_message_format(str(i)))
                    test.loop_ati_with_parameters(pin_locked)

                    test.log.step(f"{i}.2 ERROR response returns with invalid commands - port {test_port.name}")
                    invalid_params = ("=?", "?", "*", "=z", "=#", "=2", "%2", "2?", "??", "???", "????")
                    for invalid_param in invalid_params:
                        if i == 1:
                            test.expect(
                                test.dut.at1.send_and_verify("ATI{}".format(invalid_param),
                                                             "\+CME ERROR:\s+\d{1,3}"))
                        else:
                            test.expect(test.dut.at1.send_and_verify("ATI{}".format(invalid_param),
                                                                     "\+CME ERROR:\s+\w+"))

    def cleanup(test):
        pass

    def loop_ati_with_parameters(test, pin_locked):
        test.log.info("Check all ATI commands.")

        test.log.info(' 1). Check response of command "ATI".')
        ati_result = test.dut.dstl_collect_ati_information_from_other_commands()
        test.dut.at1.send_and_verify("ATI", ati_result)

        ati_params = test.dut.dstl_get_defined_ati_parameters()
        if 'undefined' in ati_params:
            test.expect(False, msg='Ati parameters are not defined for {test.dut.project}, skip tests')
        else:
            test.log.info(f"Check response of ATI with parameters {ati_params}")
        index = 2
        for ati_param in ati_params:
            test.log.info(f' {index}). Check response of command "ATI{ati_param}".')
            if ati_param == 2:
                test.expect(eval(f'test.dut.dstl_check_ati{ati_param}_response')(pin_locked))
            else:
                test.expect(eval(f'test.dut.dstl_check_ati{ati_param}_response()'))
            index += 1


if "__main__" == __name__:
    unicorn.main()
