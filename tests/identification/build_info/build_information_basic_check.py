#responsible: dan.liu@thalesgroup.com
#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0104035.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.identification import get_identification
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_airplane_mode
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.network_service import register_to_network

class Test(BaseTest):
    """
    TC0104035.001 - BuildInformationBasicCheck
    This case needs to configure all supported por
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(2)

    def run(test):
        test_ports = []
        for i in range(1,6):
            if hasattr(test.dut, 'at' + str(i)):
                port = eval(f'test.dut.at{i}')
                if port:
                    test_ports.append(port)

        test.log.step('1. Check command at^cicret without pin')
        for port in test_ports:
            test.log.info(f'Check the command cicret on {port.name} port')
            test.expect(port.send_and_verify('AT+CPIN?', '.*SIM PIN.*'))
            test.expect(port.send_and_verify('AT^CICRET=SWN', '.*OK.*'))
            cicret_resp = port.last_response
            test.expect(port.send_and_verify('AT^SOS=VER', '.*'))
            sos_ver_resp = port.last_response

        test.log.step('2. Check command at^cicret with pin')
        test.expect(test.dut.dstl_enter_pin())
        for port in test_ports:
            test.log.info(f'Check the command cicret on {port.name} port')
            test.expect(port.send_and_verify('AT+CPIN?', '.*READY.*'))
            test.expect(port.send_and_verify('AT^CICRET=SWN', cicret_resp))
            test.expect(port.send_and_verify('AT^SOS=VER', sos_ver_resp))

        test.log.step('3. Check command at^cicret invaild parameter')
        for port in test_ports:
            test.log.info(f'Check the command cicret on {port.name} port')
            test.expect(port.send_and_verify('AT^CICRET=1', '.*ERROR.*'))
            test.expect(port.send_and_verify('AT^CICRET=-2', '.*ERROR.*'))
            test.expect(port.send_and_verify('AT^CICRET=a', '.*ERROR.*'))

        test.log.step('4. Check the command ATI/cicret/siekret/sos in airplane mode')
        test.expect(test.dut.dstl_set_airplane_mode())
        for port in test_ports:
            test.log.info(f'Check the command cicret on {port.name} port')
            test.expect(port.send_and_verify('ATI','.*OK.*'))
            test.expect(port.send_and_verify('AT^CICRET=SWN', cicret_resp))
            test.expect(port.send_and_verify('AT^SOS=VER', sos_ver_resp))

    def cleanup(test):
        test.expect(test.dut.dstl_set_full_functionality_mode())

if "__main__" == __name__:
    unicorn.main()













