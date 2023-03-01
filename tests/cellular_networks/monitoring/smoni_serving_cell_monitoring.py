# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0088117.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.network_service import check_cell_monitor_parameters
from dstl.call.setup_voice_call import dstl_is_voice_call_supported


class Test(BaseTest):
    """
    TC0088117.001 - SMONI_serving_cell_monitoring
    Intention: Checking AT^SMONI command which supplies information of the serving cell.
    Subscriber: 2
    """
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.r1_phone_num = test.r1.sim.int_voice_nr
        test.support_255 = test.dut.dstl_is_enhanced_monitor_supported()
        pass

    def run(test):
        test.log.info('***Test Start***')
        test.log.info('*** Notice: for LIMSRV state, please check manually ***')
        test.log.info('1. test 2G network ')
        if test.dut.dstl_is_gsm_supported():
            test.check_2g()
        else:
            test.log.info('Not support, skip')

        test.log.info('2. test 3G network ')
        if test.dut.dstl_is_umts_supported():
            test.check_3g()
        else:
            test.log.info('Not support, skip')

        test.log.info('3. test 4G network ')
        if test.dut.dstl_is_lte_supported():
            test.check_4g()
        else:
            test.log.info('Not support, skip')
        pass

    def cleanup(test):
        test.log.info('***Test End***')
        pass

    def check_2g(test):
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_2g('SERACH')))
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT=0", ".*O.*"))
        test.sleep(20)
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_2g('LIMSRV')))
        if test.support_255:
            test.expect(test.dut.at1.send_and_verify("AT^SMONI=255",
                                                     test.dut.dstl_expect_smoni_parameter_2g('LIMSRV', True)))
        test.expect(test.dut.dstl_register_to_gsm())
        test.sleep(30)
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_2g('NOCONN')))
        if test.support_255:
            test.expect(test.dut.at1.send_and_verify("AT^SMONI=255",
                                                     test.dut.dstl_expect_smoni_parameter_2g('NOCONN', True)))
        if test.dut.dstl_is_voice_call_supported():
            test.dut.at1.send_and_verify('atd{};'.format(test.r1_phone_num))
            test.r1.at1.wait_for('RING')
            test.r1.at1.send_and_verify('ata'.format(test.r1_phone_num))
            test.sleep(3)
            test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_2g('DEDICATED')))
            if test.support_255:
                test.expect(
                    test.dut.at1.send_and_verify("AT^SMONI=255",
                                                 test.dut.dstl_expect_smoni_parameter_2g('DEDICATED', True)))
            test.dut.at1.send_and_verify('ath')
        pass

    def check_3g(test):
        test.dut.dstl_restart()
        test.attempt(test.dut.at1.send_and_verify, "AT^SMONI",
                     test.dut.dstl_expect_smoni_parameter_3g('SERACH'), retry=7, sleep=2)
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT=2", ".*OK.*"))
        test.sleep(20)
        test.attempt(test.dut.at1.send_and_verify, "AT^SMONI",
                     test.dut.dstl_expect_smoni_parameter_3g('LIMSRV'), retry=7, sleep=2)
        if test.support_255:
            test.expect(test.dut.at1.send_and_verify("AT^SMONI=255",
                                                     test.dut.dstl_expect_smoni_parameter_3g('LIMSRV', True)))
        test.expect(test.dut.dstl_register_to_umts())
        test.sleep(40)
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_3g('NOCONN')))
        if test.support_255:
            test.expect(
                test.dut.at1.send_and_verify("AT^SMONI=255", test.dut.dstl_expect_smoni_parameter_3g('NOCONN', True)))
        if test.dut.dstl_is_voice_call_supported():
            test.dut.at1.send_and_verify('atd{};'.format(test.r1_phone_num))
            test.r1.at1.wait_for('RING')
            test.r1.at1.send_and_verify('ata'.format(test.r1_phone_num))
            test.sleep(3)
            test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_3g('CONN')))
            if test.support_255:
                test.expect(
                    test.dut.at1.send_and_verify("AT^SMONI=255", test.dut.dstl_expect_smoni_parameter_3g('CONN', True)))
        pass

    def check_4g(test):
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_4g('SERACH')))
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT=3", ".*OK.*"))
        test.sleep(30)
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_4g('LIMSRV')))
        if test.support_255:
            test.expect(test.dut.at1.send_and_verify("AT^SMONI=255",
                                                     test.dut.dstl_expect_smoni_parameter_4g('LIMSRV', True)))
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_4g('CONN')))
        if test.support_255:
            test.expect(
                test.dut.at1.send_and_verify("AT^SMONI=255", test.dut.dstl_expect_smoni_parameter_4g('CONN', True)))
        test.sleep(300)
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", test.dut.dstl_expect_smoni_parameter_4g('NOCONN')))
        if test.support_255:
            test.expect(
                test.dut.at1.send_and_verify("AT^SMONI=255", test.dut.dstl_expect_smoni_parameter_4g('NOCONN', True)))
        pass


if "__main__" == __name__:
    unicorn.main()
