# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0107426.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """To check if  few Https connections and download big amount of data is possible."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.h2("Executing script for test case: 'TC0107426.001 - HTTPsConnectionGetBigContent'")

        test.log.step("1. Define and activate PDP context / connection Profile")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())
        test.expect(test.connection_setup.dstl_activate_internet_connection(), critical=True)

        test.log.step("2. Define 6 HTTPs profiles to different sites with secopt 0 (where content "
                      "to download it's "
                      "from 1KB to few MB's)")
        profiles = []
        addresses = ["archive.org/download/eFilingComics/17_Tintin_and_the_Explorers_on_the_Moon_"
                     "abbyy.gz",
                     "httpbin.org/stream-bytes/1024", "google.com", "reddit.com",
                     "en.wikipedia.org/wiki/List_of_Warriors_characters", "wp.pl"]

        for profile_number in range(6):
            profiles.append(HttpProfile(test.dut, profile_number,
                                        test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                        http_command="get", host=addresses[profile_number],
                                        ip_version="ipv4", secopt="0", secure_connection=True))
            profiles[profile_number].dstl_generate_address()
            test.expect(profiles[profile_number].dstl_get_service().dstl_load_profile())

        for profile_number in range(0, 6, 2):
            test.log.step("Open and establish all HTTPs connection (On Serval due the memory "
                          "limitation max 2 profiles "
                          "should be opened at the same time)")
            test.expect(profiles[profile_number].dstl_get_service().dstl_open_service_profile())
            test.expect(profiles[profile_number+1].dstl_get_service().dstl_open_service_profile())

            test.log.step("5. Check URC shows that data can be read (done in previous step)")

            test.log.step("6. Read all data from server")
            data_first_profile = ""
            data_second_profile = ""
            while "SISR: {},-2".format(profile_number) not in test.dut.at1.last_response:
                data_first_profile += profiles[profile_number].dstl_get_service().\
                    dstl_read_return_data("1500")

            while "SISR: {},-2".format(profile_number+1) not in test.dut.at1.last_response:
                data_second_profile += profiles[profile_number+1].dstl_get_service().\
                    dstl_read_return_data("1500")

            test.log.step("7. Check sevice states and RX/TX counters using SISO command")
            test.expect(profiles[profile_number].dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.DOWN.value)
            test.expect(profiles[profile_number].dstl_get_parser().
                        dstl_get_service_data_counter("rx") >= len(data_first_profile))

            test.expect(profiles[profile_number+1].dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.DOWN.value)
            test.expect(profiles[profile_number+1].dstl_get_parser().
                        dstl_get_service_data_counter("rx") >= len(data_second_profile))

            test.log.step("8. Close connections")
            test.expect(profiles[profile_number].dstl_get_service().dstl_close_service_profile())
            test.expect(profiles[profile_number + 1].dstl_get_service().
                        dstl_close_service_profile())

    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
