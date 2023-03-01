#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0092754.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.configuration import functionality_modes
from dstl.security import get_spic_facility


class Test(BaseTest):
    """ TC0092754.001 - TpAtSpicBasic   """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(5)

    def run(test):
        test.log.info("1.1 Check parameter without PIN")
        test.check_command()

        test.log.info("1.2 Check parameter with PIN")
        test.expect(test.dut.dstl_enter_pin())
        test.check_command()

        test.log.info("2. Check parameter in airplane mode")
        test.dut.dstl_set_airplane_mode()
        test.check_command()
        test.dut.dstl_set_full_functionality_mode()

        test.log.info("3. Check invalid parameters")
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=-1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",!!!", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=0,\"SC\"", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=abc", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC!", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"PS\",0,0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",0,\"1234\"", ".*ERROR.*"))


    def cleanup(test):
        pass

    def check_command(test):

        test.expect(test.dut.at1.send_and_verify("AT^SPIC=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", ".*\^SPIC:.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC:.*OK.*"))
        f_list =test.dut.dstl_supported_spic_facility()
        for facility_value in f_list :
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"{}\"".format(facility_value), ".*\^SPIC:.*OK.*"))
            if facility_value == 'SC' or facility_value == 'P2':
                test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"{}\",0".format(facility_value), ".*\^SPIC:.*OK.*"))
                test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"{}\",1".format(facility_value), ".*\^SPIC:.*OK.*"))




if "__main__" == __name__:
    unicorn.main()
