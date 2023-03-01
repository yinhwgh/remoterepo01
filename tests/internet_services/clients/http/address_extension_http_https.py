# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0105926.001, TC0105926.002


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.http_otap_server import HttpOtapServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Intention:
    Intention of this TC is to verify http and https functionality of address extension

    Description:
    1. Attach Module to Network.
    2. Define HTTP "get" internet profile with extended address length. The whole address should be
     divided into address, address2, address3, and address4 parameters.
    3. Open defined profile.
    4. Check service and socket state using SISO command.
    5. Try to download page content (at least 100 bytes).
    6. Check service and socket state using SISO command.
    7. Close HTTP profile.
    8. Repeat steps 2-7 for HTTPS "get".
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.long_path = "/1111111111111111111111111111111111111111111111111111111111111111111111" \
                         "11111111111111111111111111111111111111111111111111111111111111111111111" \
                         "11111111111111111111111111111111111111111111111111111111111111111111111" \
                         "1111111111111111111111111111111111111111111/222222222222222222222222222" \
                         "22222222222222222222222222222222222222222222222222222222222222222222222" \
                         "22222222222222222222222222222222222222222222222222222222222222222222222" \
                         "22222222222222222222222222222222222222222222222222222222222222222222222" \
                         "222222222222222/3333333333333333333333333333333333333333333333333333333" \
                         "33333333333333333333333333333333333333333333333333333333333333333333333" \
                         "33333333333333333333333333333333333333333333333333333333333333333333333" \
                         "3333333333333333333333333333333333333333333333333333333333/444444444444" \
                         "44444444444444444444444444444444444444444444444444444444444444444444444" \
                         "44444444444444444444444444444444444444444444444444444444444444444444444" \
                         "44444444444444444444444444444444444444444444444444444444444444444444444" \
                         "444444444444444444444444444444/5555555555555555555555555555555555555555" \
                         "55555555555555555555555555555555555555555555555555555555555555555555555" \
                         "55555555555555555555555555555555555555555555555555555555555555555555555" \
                         "55555555555555555555555555555555555555555555555555555555555555555555555" \
                         "55/66666666666666666666666666666666666666666666666666666666666666666666" \
                         "66666666666666666666666666666666666666666666666666666666666666666666666" \
                         "66666666666666666666666666666666666666666666666666666666666666666666666" \
                         "666666666666666666666666666666666666666666666/7777777777777777777777777" \
                         "77777777777777777777777777777777777777777777777777777777777777777777777" \
                         "77777777777777777777777777777777777777777777777777777777777777777777777" \
                         "77777777777777777777777777777777777777777777777777777777777777777777777" \
                         "77777777777777777/100kB.txt"
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.http_server = HttpOtapServer("IPv4")
        test.http_addr = str(test.http_server.dstl_get_server_ip_address())
        test.http_port = str(test.http_server.dstl_get_server_port())
        test.http_long = "http://" + test.http_addr + ":" + test.http_port + test.long_path
        test.https_long = "https://httpbin.org/get"

    def run(test):
        test.log.info("TC0105926.00X address_extension_http_https")
        test.log.step("1. Attach Module to Network")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define HTTP ""get"" internet profile with extended address length. The"
                    " whole address should be divided into address, address2, address3,"
                    " and address4 parameters.")

        test.http_client = HttpProfile(test.dut, '0', connection_setup.dstl_get_used_cid(),
                            http_command="get", address=test.http_long[0:511],
                            address2=test.http_long[511:1022], address3=test.http_long[1022:1533],
                            address4=test.http_long[1533:])
        test.expect(test.http_client.dstl_get_service().dstl_load_profile())
        test.service_checking(test.http_client)

        test.log.step("8. Repeat steps 2-7 for HTTPS ""get"". ")
        test.log.step("2. Define HTTP ""get"" internet profile with extended address length. "
                      "The whole address should be divided into address, address2, address3, "
                      "and address4 parameters.")
        test.https_client = HttpProfile(test.dut, '1', connection_setup.dstl_get_used_cid(),
                            http_command="get", address=test.https_long[0:10],
                            address2=test.https_long[10:12], address3=test.https_long[12:15],
                            address4=test.https_long[15:], secure_connection=True, secopt="0")
        test.expect(test.https_client.dstl_get_service().dstl_load_profile())
        test.service_checking(test.https_client)

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.http_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.http_client.dstl_get_service().dstl_reset_service_profile())
            test.expect(test.https_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.https_client.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")

    def service_checking(test, used_profile):
        test.log.step("3. Open defined profile.")
        test.expect(used_profile.dstl_get_service().dstl_open_service_profile())

        test.log.step("4. Check service and socket state using SISO command.")
        test.expect(used_profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(used_profile.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)

        test.log.step("5. Try to download page content (at least 100 bytes)")
        used_profile.dstl_get_service().dstl_read_data(200)

        test.log.step("6. Check service and socket state using SISO command.")
        test.expect(used_profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(used_profile.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)

        test.log.step("7. Close HTTP profile")
        test.expect(used_profile.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()