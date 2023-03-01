#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0093676.001, TC0093676.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """	Check the behaviour of module when there's no empty service profile slots."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))


    def run(test):
        test.log.step("1) Depends on product:\r\n"
                      " - Setup Internet Connection Profile (GPRS)\r\n"
                      "- Define and activate PDP context\r\n")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))
        test.listener_profiles_dut = []

        test.conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.conn_setup_dut.dstl_load_and_activate_internet_connection_profile())
        conn_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(conn_setup_r1.dstl_load_and_activate_internet_connection_profile())

        for listener_amount in range(1, 10):

            test.log.info("Now Running for option:\r\n"
                          "- {} listeners and {} profiles occupied by clients created by listener(s) (active connection"
                          "bis not required),\r\n".format(listener_amount, 10-listener_amount))

            test.log.step("2) Set and open service profile: TCP non transparent listener on DUT .")
            dstl_reset_internet_service_profiles(test.dut, force_reset=True)
            test.load_listeners(listener_amount)

            test.expect(test.listener_profiles_dut[0].dstl_get_service().dstl_open_service_profile())
            test.expect(test.listener_profiles_dut[0].dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

            dut_ip_address_and_port = test.listener_profiles_dut[0].dstl_get_parser(). \
                dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")

            test.log.step("3) Set and open service profile: TCP non transparent client on Remote.")
            test.socket_remote = SocketProfile(test.r1, 0, conn_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                               host=dut_ip_address_and_port[0], port=dut_ip_address_and_port[1])
            test.socket_remote.dstl_generate_address()
            test.expect(test.socket_remote.dstl_get_service().dstl_load_profile())
            test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_remote.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

            test.log.step("4) Accept incoming connection on DUT.")
            test.expect(test.listener_profiles_dut[0].dstl_get_urc().dstl_is_sis_urc_appeared('1'))
            client_srv_id = test.listener_profiles_dut[0].dstl_get_urc().dstl_get_sis_urc_info_id()

            test.server_dut = SocketProfile(test.dut, client_srv_id, test.conn_setup_dut.dstl_get_used_cid())
            test.expect(test.server_dut.dstl_get_service().dstl_open_service_profile())

            test.log.step("5) Wait for write URC on client.")
            test.log.info("done in step 3")

            test.log.step("6) Close service on Remote.")
            test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())

            test.expect(test.server_dut.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause='0', urc_info_id="48"))
            test.dut.at1.read() #clearing buffer of this URC

            for profile_id in range(1 + listener_amount, 10):

                test.log.step("7) Open again connection on Remote.")
                test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile())
                test.expect(test.socket_remote.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

                test.log.step("8) Accept incoming connection on DUT.")
                test.expect(test.listener_profiles_dut[0].dstl_get_urc().dstl_is_sis_urc_appeared('1'))
                client_srv_id = test.listener_profiles_dut[0].dstl_get_urc().dstl_get_sis_urc_info_id()

                test.server_dut = SocketProfile(test.dut, client_srv_id, test.conn_setup_dut.dstl_get_used_cid())
                test.expect(test.server_dut.dstl_get_service().dstl_open_service_profile())

                test.log.step("9) Wait for write URC on client.")
                test.log.info("done in step 7")

                test.log.step("10) Close service on Remote.")
                test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())
                test.expect(test.server_dut.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause='0', urc_info_id="48"))
                test.dut.at1.read()  # clearing buffer of this URC

                test.log.step("11) Repeat steps 7-10 until all profiles are occupied."
                              "\r\nAlready repeated  for profile number {}.".format(profile_id))

            test.log.step("12) Open connection on Remote once more time.")
            test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
            test.expect(test.socket_remote.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause='0', urc_info_id="48"))

            test.log.step("13) Close connection on Remote.")
            test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())


            test.log.step("14) Whole test should be repeated for each following option: \r\n"
                          "- 2 listeners and 8 profiles occupied by clients created by listener(s) (active connection "
                          "is not required),\r\n"
                          "- 3 listeners and 7 profiles occupied by clients created by listener(s) (active connection "
                          "is not required),\r\n"
                          "- 4 listeners and 6 profiles occupied by clients created by listener(s) (active connection "
                          "is not required),\r\n"
                          "- 5 listeners and 5 profiles occupied by clients created by listener(s) (active connection "
                          "is not required),\r\n"
                          "- 6 listeners and 4 profiles occupied by clients created by listener(s) (active connection "
                          "is not required),\r\n"
                          "- 7 listeners and 3 profiles occupied by clients created by listener(s) (active connection "
                          "is not required),\r\n"
                          "- 8 listeners and 2 profiles occupied by clients created by listener(s) (active connection "
                          "is not required),\r\n"
                          "- 9 listeners and 1 profiles occupied by clients created by listener(s) (active connection "
                          "is not required).\r\n")

    def cleanup(test):
        try:
            dstl_reset_internet_service_profiles(test.r1, force_reset=True)
        except AttributeError:
            test.log.error("Problem with conenction to module")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


    def load_listeners(test, amount):
        for i in range(amount):
            test.socket_listener = SocketProfile(test.dut, i, test.conn_setup_dut.dstl_get_used_cid(),
                                                 protocol="tcp", host="listener", localport="888{}".format(i))
            test.socket_listener.dstl_generate_address()
            test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())
            test.listener_profiles_dut.append(test.socket_listener)


if "__main__" == __name__:
    unicorn.main()
