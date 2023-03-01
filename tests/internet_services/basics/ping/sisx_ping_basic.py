# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107966.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution


class Test(BaseTest):
    """
    Intention:
    To check basic PING feature using SISX command

    Description:
    1. Power on Modul and enter PIN
    2. Depends on Module:
    - define pdp context/nv bearer using CGDCONT command and activate it using SICA command
    - define Connection Profile using SICS command
    3. Check write command with basic set of parameters (e.g. AT^SISX="ping",1,"8.8.8.8")
    4. Check write command with all correct parameters (e.g. AT^SISX="ping",1,"8.8.8.8",10,6000)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.ip_address = "8.8.8.8"
        test.ping_requests = 10
        test.ping_limit = 6000

    def run(test):
        test.log.info("TC0107966.001 SisxPingBasic")
        test.log.step('1. Power on Modul and enter PIN')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_enter_pin(test.dut)
        test.sleep(10)

        test.log.step('2) Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                      'command and activate it using SICA command\r\n'
                      '- define Connection Profile using SICS command')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()

        test.log.step('3. Check write command with basic set of parameters '
                      '(e.g. AT^SISX="ping",1,"8.8.8.8")')
        test.ping_execution = InternetServiceExecution(test.dut, test.cid)
        test.expect(test.ping_execution.dstl_execute_ping(test.ip_address, expected_response="OK"))

        test.log.step('4. Check write command with all correct parameters '
                      '(e.g. AT^SISX="ping",1,"8.8.8.8",10,6000)')
        test.expect(test.ping_execution.dstl_execute_ping(test.ip_address,
                                                          request=test.ping_requests,
                                                          timelimit=test.ping_limit,
                                                          expected_response="OK"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()