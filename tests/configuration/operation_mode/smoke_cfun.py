# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0095489.001, TC0096525.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """Simple check of Restart the module with and without Registration."""

    def setup(test):
        test.log.step("- start the module")
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        if test.cfun_loops_without_registration == 25:
            test.log.h2("Executing script for test case: 'SmokeCfun50'")
        else:
            test.log.h2("Executing script for test case: 'SmokeCfun'")

        test.log.step("make in a loop {} times\r\n- restart module with cfun"
                      .format(test.cfun_loops_without_registration))
        for iteration in range(test.cfun_loops_without_registration):
            test.log.info('Iteration no. {}'.format(iteration+1))
            test.expect(dstl_restart(test.dut))

        test.log.step("make in a loop {} times\r\n- restart the module with cfun\r\n"
                      "- register into Network\r\n- check SIM"
                      .format(test.cfun_loops_with_registration))
        for iteration in range(test.cfun_loops_with_registration):
            test.log.info('Iteration no. {}'.format(iteration + 1))
            test.expect(dstl_restart(test.dut))
            test.sleep(5)
            test.expect(dstl_register_to_network(test.dut))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
