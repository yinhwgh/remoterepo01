# responsible: michal.kopiel@globallogic.com
# location: Wroclaw
# TC0087352.002

from typing import Union

import unicorn
from core.basetest import BaseTest

from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_check_no_internet_profiles_defined import \
    dstl_check_no_internet_profiles_defined
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.internet_service.profile_storage.dstl_execute_sips_command import \
    dstl_execute_sips_command


class Test(BaseTest):
    '''
    Do the following scenario at MUX1, MUX2 and MUX3:
    1. Define a connection profile and a service profile with a minimum set of parameters.
    2. Display all profiles
    3. Save the profiles to storage.
    4. Switch off the DUT, wait 10 seconds and switch on the DUT.
    5. Enter the PIN.
    6. Display all profiles
    7. Load one undefined connection profile and one undefined service profile.
    8. Display all profiles.
    9. Load the defined connection profile.
    10. Display all profiles.
    11. Load the defined service profile.
    12. Display all profiles.
    13. Reset the reloaded connection profile.
    14. Display all profiles.
    15. Reset the reloaded service profile.
    16. Display all profiles.
    '''

    def setup(test):
        test.srv_id_0 = '0'
        test.srv_id_1 = '1'
        test.con_id = '1'

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

        test.dut.at1.close()
        test.sleep(10)

    def run(test):
        mux_interfaces = ['dut_mux_1', 'dut_mux_2', 'dut_mux_3']

        for mux_interface in mux_interfaces:
            test.remap({'dut_at1': mux_interface})
            if mux_interface != 'dut_mux_3':
                test.log.step("Do the following scenario on next MUX interface")

            test.log.step('1. Define a connection profile and a service'
                          ' profile with a minimum set of parameters.')
            test.http_profile = HttpProfile(test.dut, test.srv_id_0, test.con_id,
                                            address="http://test123", http_command="head")
            test.expect(test.http_profile.dstl_get_service().dstl_load_profile())

            test.log.step('2. Display all profiles')
            dstl_check_siss_read_response(test.dut, [test.http_profile])

            test.log.step('3. Save the profiles to storage')
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'save'))

            test.log.step('4. Switch off the DUT, wait 10 seconds and switch on the DUT.')
            test.expect(dstl_restart(test.dut))
            test.sleep(30)  ###to give module time to enable SIM

            test.log.step('5. Enter the PIN.')
            test.expect(dstl_enter_pin(test.dut))

            test.log.step('6. Display all profiles')
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step(
                '7. Load one undefined connection profile and one undefined service profile.')
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'load', test.srv_id_1))

            test.log.step('8. Display all profiles')
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step('9. Load the defined connection profile.')
            test.log.info("SIPS command does not support connection profiles on Viper")

            test.log.step('10. Display all profiles')
            test.log.info("SIPS command does not support connection profiles on Viper")

            test.log.step('11. Load the defined service profile.')
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'load', test.srv_id_0))

            test.log.step('12. Display all profiles')
            dstl_check_siss_read_response(test.dut, [test.http_profile])

            test.log.step('13. Reset the reloaded connection profile.')
            test.log.info("SIPS command does not support connection profiles on Viper")

            test.log.step('14. Display all profiles')
            test.log.info("SIPS command does not support connection profiles on Viper")
            test.log.info("Only service profiles will be check")
            dstl_check_siss_read_response(test.dut, [test.http_profile])

            test.log.step('15. Reset the reloaded service profile.')
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'reset'))

            test.log.step('16. Display all profiles')
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))
        test.expect(dstl_execute_sips_command(test.dut, 'service', 'save'))


if "__main__" == __name__:
    unicorn.main()
