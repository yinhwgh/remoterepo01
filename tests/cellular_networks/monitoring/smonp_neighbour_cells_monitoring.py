#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0088118.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.network_service import check_cell_monitor_parameters
class Test(BaseTest):
    '''
    TC0088118.001 - SMONP_neighbour_cells_monitoring
    Intention: Checking AT^SMONP command which supplies information of 3G active cells and all neighbour cells.
    Subscriber: 1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_enter_pin()
        test.sim_imsi = str(test.dut.sim.imsi)
        test.support_255 = test.dut.dstl_is_enhanced_monitor_supported()

    def run(test):

        test.log.info('***Test Start***')
        test.log.info('1. test 2G network ')

        if test.dut.dstl_is_gsm_supported():
            test.check_2g(test.support_255)
        else:
            test.log.info('Not support 2G, skip')

        test.log.info('2. test 3G network ')
        if test.dut.dstl_is_umts_supported():
            test.check_3g(test.support_255)
        else:
            test.log.info('Not support 3G, skip')


        # 4G will be tested in TC0088118.002


    def cleanup(test):
       test.log.info('***Test End***')

    def check_2g(test,test_enhanced):
        register_result = test.dut.dstl_register_to_gsm()
        if register_result:
            test.sleep(30)
            smonp_res = test.dut.dstl_expect_smonp_parameter_2g()
            test.expect(test.dut.at1.send_and_verify("AT^SMONP", smonp_res))

            if test_enhanced:
                smonp255_res = test.dut.dstl_expect_smonp_parameter_2g(enhanced=True)
                test.expect(test.dut.at1.send_and_verify("AT^SMONP=255", smonp255_res))
        else:
            test.log.error('Register to network error, please check network condition!')
            test.expect(False)

    def check_3g(test,test_enhanced):
        register_result = test.dut.dstl_register_to_umts()
        if register_result:
            test.sleep(30)
            smonp_res = test.dut.dstl_expect_smonp_parameter_3g()
            test.expect(test.dut.at1.send_and_verify("AT^SMONP", smonp_res))

            if test_enhanced:
                smonp255_res = test.dut.dstl_expect_smonp_parameter_3g(enhanced=True)
                test.expect(test.dut.at1.send_and_verify("AT^SMONP=255", smonp255_res))
        else:
            test.log.error('Register to network error, please check network condition!')
            test.expect(False)


if "__main__" == __name__:
    unicorn.main()

