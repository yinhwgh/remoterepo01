#responsible: fang.liu@globallogic.com
#location: Berlin
#TC0085497.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.security.lock_unlock_sim import *

class Test(BaseTest):

    def setup(test):
        """
        Steps:
        1. Configure 16 different PDP contexts;
        2. Check the configuration of all PDP contexts;
        3. Activate one of the configured PDP context;
        4. Check the state of all configured PDP contexts;
        5. Try to activate each of the other PDP contexts and check the state of all configured PDP contexts
        6. Deactivate the active PDP context;
        7. Repeat the three steps above for all configured PDP contexts;
        8. Delete all PDP contexts;
        9. Check the configuration of all PDP contexts.
        """
        test.dut.dstl_detect()
        test.dut.dstl_unlock_sim()

    def run(test):

        test.dut.at1.send_and_verify("at+cgdcont=?", ".*OK.*")

        pdp_type = ["IP", "IPV4V6", "IPV6", "PPP"]

        for item in pdp_type:
            i = 4
            while i <= 16:
                test.dut.at1.send_and_verify("at+cgdcont={},\"{}\",\"\"".format(i, item), ".*OK.*")
                test.dut.at1.send_and_verify("at+cgact=1,{}".format(i), ".*OK.*")
                test.sleep(5)
                test.dut.at1.send_and_verify("at+cgact?", "+CGACT: {},1".format(i))
                test.dut.at1.send_and_verify("at+cgact=0,{}".format(i), ".*OK.*")
                i = i+1
                test.sleep(5)

            test.dut.at1.send_and_verify("at+cgdcont?", ".*OK.*")


    def cleanup(test):
        """
        Delete these PDP contexts after test.
        """
        i = 4
        while i <= 16:
            test.dut.at1.send_and_verify("at+cgdcont={},\"IPV4V6\",\"\"".format(i), ".*OK.*")
            test.dut.at1.send_and_verify("at+cgact=0,{}".format(i), ".*OK.*")
            i = i+1
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
