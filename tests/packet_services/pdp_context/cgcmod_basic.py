#responsible: baris.kildi@thalesgroup.com
#location: Berlin
#TC0087417.002

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object



class Test(BaseTest):

    """"
    Prove the correct implementation of the AT command +CGCMOD
    """

    def setup(test):

        test.dut.dstl_detect()

    def run(test):
        test.log.info("1. Restart module and enable error result code with verbose (string) values ")
        test.dut.dstl_restart()
        test.dut.at1.send_and_verify('AT+CMEE=2', '.*\sOK\s.*')
        test.dut.at1.send_and_verify('AT+CPIN?', '.*\sOK\s.*')

        test.log.info("2. Enter the test command (shall be rejected, because the command is PIN protected) ")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=?', '.*CME ERROR: SIM PIN required.*'))

        test.dut.dstl_enter_pin()

        test.log.info("3. Enter the test command (shall be accepted and an empty list shall be returned")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=?', '+CGCMOD: ()'))

        test.log.info("4. Enter the write command without parameters")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=', '+CME ERROR: Incorrect parameters.*'))

        test.log.info("5. Enter the write command with every possible context ID")

        if (test.dut.product == 'cougar'):
            for i in range(1, 9):
                test.expect(test.dut.at1.send_and_verify('AT+CGCMOD={}'.format(i), '+CME ERROR: invalid index.*'))
        else:
            for i in range(1, 17):
                test.expect(test.dut.at1.send_and_verify('AT+CGCMOD={}'.format(i), '+CME ERROR: invalid index.*'))

        test.log.info("6. Enter the write command with some subsequent and non-subsequent context IDs")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=1,6', '+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=6,7', '+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=8,1', '+CME ERROR: invalid index.*'))

        test.log.info("7. Define PDP context")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version="IPV4V6", ip_public=False)
        test.expect(connection_setup_dut.dstl_define_pdp_context())

        test.log.info("8. Enter the test command (shall be accepted and an empty list shall be returned")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=?', '+CGCMOD: ()'))

        test.log.info("9. Enter the write command without parameters")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=', '+CME ERROR: Incorrect parameters.*'))

        test.log.info("10. Enter the write command with every possible context ID")

        if (test.dut.product == 'cougar'):
            for i in range(1, 9):
                test.expect(test.dut.at1.send_and_verify('AT+CGCMOD={}'.format(i), '+CME ERROR: invalid index.*'))
        else:
            for i in range(1, 17):
                test.expect(test.dut.at1.send_and_verify('AT+CGCMOD={}'.format(i), '+CME ERROR: invalid index.*'))

        test.log.info("11. Enter the write command with some subsequent and non-subsequent context IDs")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=1,6', '+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=6,7', '+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=8,1', '+CME ERROR: invalid index.*'))

        test.log.info("12. Activate PDP context")
        test.expect(connection_setup_dut.dstl_activate_pdp_context())

        test.log.info("13. Check if PDP context is active")
        test.expect(connection_setup_dut.dstl_get_pdp_address())

        test.log.info("14. Enter the test command (the ID of the activated PDP context shall be returned)")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=?', '+CGCMOD: (1)'))

        test.log.info("15. Enter the write command without parameters")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=', '+CME ERROR: Incorrect parameters.*'))

        test.log.info("16. Enter the write command with every possible context ID")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=1', '.*\sOK\s.*'))

        if (test.dut.product == 'cougar'):
            for i in range(2, 9):
                test.expect(test.dut.at1.send_and_verify('AT+CGCMOD={}'.format(i), '+CME ERROR: invalid index.*'))
        else:
            for i in range(2, 17):
                test.expect(test.dut.at1.send_and_verify('AT+CGCMOD={}'.format(i), '+CME ERROR: invalid index.*'))


        test.log.info("17. Enter the write command with some subsequent and non-subsequent context IDs")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=1,6', '+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=6,7', '+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=8,1', '+CME ERROR: invalid index.*'))

        test.log.info("4. Deactivate PDP context")
        test.expect(connection_setup_dut.dstl_deactivate_pdp_context())



    def cleanup(test):

        pass


if "__main__" == __name__:
    unicorn.main()
