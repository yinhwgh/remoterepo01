#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0088118.002


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.network_service import check_cell_monitor_parameters
class Test(BaseTest):
    '''
    TC0088118.002 - SMONP_neighbour_cells_monitoring
    Intention: Checking AT^SMONP command which supplies information of 4G active cells and all neighbour cells.
    Subscriber: 1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.support_255 = test.dut.dstl_is_enhanced_monitor_supported()

    def run(test):

        test.log.info('***Test Start***')
        test.log.info('Attach module to 4G Network, use AT^SMONP and AT^SMONP=255 command. ')

        if test.dut.dstl_is_lte_supported():
            test.check_4g(test.support_255)
        else:
            test.log.info('Not support 4G, skip')

        test.check_4g(test.support_255)


    def cleanup(test):
       test.log.info('***Test End***')

    def check_4g(test,test_enhanced):
        register_result = test.dut.dstl_register_to_lte()
        test.sleep(30)

        if register_result:
            smonp_res= test.dut.dstl_expect_smonp_parameter_4g()
            test.expect(test.dut.at1.send_and_verify("AT^SMONP", smonp_res))

            if test_enhanced:
                smonp255_res = test.dut.dstl_expect_smonp_parameter_4g(enhanced=True)
                test.expect(test.dut.at1.send_and_verify("AT^SMONP=255", smonp255_res))
        else:
            test.log.error('Register to network error, please check network condition!')
            test.expect(False)



if "__main__" == __name__:
    unicorn.main()

