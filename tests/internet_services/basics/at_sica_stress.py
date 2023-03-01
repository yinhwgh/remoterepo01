#responsible: qing.shen@thalesgroup.com
#location: Beijing
#TC0105923.001
#Hints:




import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object

'''
Case name: TC0106040.001 AtSica_stress
'''


class address_extension_basic(BaseTest):
    def __init__(self):
        super().__init__()


    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()


    def run(test):
        test.log.info('---------Test Begin -------------------------------------------------------------')

        test.log.step('1 Define one PDP context usting AT+CGDCONT')
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_define_pdp_context())

        test.log.step("2. Repeat steps 3-4 in a loop of 100 iteration")
        for i in range(100):
            test.log.step('3 .Activate the Internet Connection which defined in step1 using AT^SICA=1,x at {} time'.format(i))
            test.expect(test.dut.at1.send_and_verify('at^sica=1,1', 'OK'))


            test.log.step('4 .Deactivate the Internet Connection using AT^SICA=0,x at {}'.format(i))
            test.expect(connection_setup.dstl_deactivate_internet_connection())
            test.expect(test.dut.at1.send_and_verify('AT^SMONI','.*'))

        test.log.info('---------Test End -------------------------------------------------------------')

    def cleanup(test):
        pass


if (__name__ == '__main__'):
    unicorn.main()
