# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0095210.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.network_service import check_cell_monitor_parameters
from dstl.configuration import set_autoattach
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):
    """
    TC0095210.001 - SMONI_GPRS_status
    Intention: Checking AT^SMONI command which GPRS status of the serving cell.
    This test case was designed due to IPIS100109822
    Subscriber: 1
    """
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        pass

    def run(test):
        test.log.info('***Test Start***')
        test.log.info('1.Disable the GPRS auto attach function and restart module')
        test.dut.dstl_disable_ps_autoattach()
        test.dut.dstl_restart()
        test.sleep(5)
        test.step2to6(False)

        test.log.info('7.Repeat step 2-6 and check GPRS status with GPRS/AutoAttach enable.')
        test.dut.dstl_enable_ps_autoattach()
        test.dut.dstl_restart()
        test.sleep(5)
        test.step2to6(True)
        pass

    def cleanup(test):
        test.log.info('***Test End***')
        test.dut.dstl_register_to_network()
        pass

    def step2to6(test, auto_attach_status):
        expect_response_attach = 'SMONI: 2G,.*,[G|E],.*'
        expect_response_disattach = 'SMONI: 2G,.*,-,.*'

        test.log.info('2.Enter PIN code to register on network.')
        # test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_gsm()
        test.sleep(10)
        if not auto_attach_status:
            test.log.info('1.3.Check result of at+cgatt? to ensure GPRS is not attached.')
            test.expect(test.dut.at1.send_and_verify('at+cgatt?', 'CGATT: 0'))

            test.log.info('1.4.Check GPRS status is correct by command at^smoni.')
            test.expect(test.dut.at1.send_and_verify('at^smoni', expect_response_disattach))

            test.log.info('1.5.Activate GPRS attach at+cgatt=1')
            test.expect(test.dut.at1.send_and_verify('at+cgatt=1', 'OK'))
            test.sleep(3)
            test.log.info('1.6.Check GPRS status again, to ensure the status is same as step 4.')

            test.attempt(test.dut.at1.send_and_verify, 'at^smoni', expect_response_attach, retry=5, sleep=2)

        else:
            test.log.info('7.3.Check result of at+cgatt? to ensure GPRS is  attached.')
            test.expect(test.dut.at1.send_and_verify('at+cgatt?', 'CGATT: 1'))

            test.log.info('7.4.Check GPRS status is correct by command at^smoni.')
            test.expect(test.dut.at1.send_and_verify('at^smoni', expect_response_attach))

            test.log.info('7.5.Deactivate GPRS attach at+cgatt=1')
            test.expect(test.dut.at1.send_and_verify('at+cgatt=0', 'OK'))
            test.sleep(3)
            test.log.info('7.6.Check GPRS status again, to ensure the status is same as step 4.')
            test.expect(test.dut.at1.send_and_verify('at^smoni', expect_response_disattach))

        return


if "__main__" == __name__:
    unicorn.main()
