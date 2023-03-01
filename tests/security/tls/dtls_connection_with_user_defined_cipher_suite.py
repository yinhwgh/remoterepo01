#responsible: lukasz.lidzba@globallogic.com
#location: Wroclaw
#TC0102413.002, TC0102413.001

import unicorn


from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.profile_storage.dstl_execute_sips_command import dstl_execute_sips_command


class Test(BaseTest):
    """
    To check if user defined list of available cipher suites can be properly set and if connection to server can be
    established only for defined cipher suite(s)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.step("1. Activate certificate 'CIEV:' indicator")
        test.expect(test.dut.at1.send_and_verify('at^sind="is_cert",1'))

        test.log.step("2. Display a list of cipher suites supported by module")
        test.expect(test.dut.at1.send_and_verify('at^sbnr="ciphersuites","default"'))

        test.log.step("3.Select and copy one of supported cipher suites from the list. Make sure you copy only the "
                      "name, without spaces or colon(s) (i.e. AES128-SHA). Count a number of characters of cipher "
                      "suite name (=10 for the given example).")
        supported_ciphers = test.dut.at1.last_response.split(":")
        chosen_cipher = supported_ciphers[7]

        test.log.step("4. Set the user defined list of available cipher suites.")
        test.dut.at1.send('at^sbnw="ciphersuites",{}'.format(len(chosen_cipher)))
        test.sleep(3)
        test.dut.at1.send(chosen_cipher, end="")
        test.expect(test.dut.at1.wait_for(".*OK.*"))

        test.log.step("5. Restart module and enter PIN")
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("6. Display current set (user defined list) of cipher suites.")
        test.expect(test.dut.at1.send_and_verify('at^sbnr="ciphersuites","current"', expect=chosen_cipher))
        test.expect(":" not in test.dut.at1.last_response)

        test.log.step("7. Remove certificates from module if any installed.")
        test.certificates = OpenSslCertificates(test.dut, 1)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            test.certificates.dstl_delete_all_uploaded_certificates()

        test.log.step("8. Run OpenSSL server with one cipher suite chosen in step 3")
        test.ssl_server = SslServer("IPv4", "dtls", chosen_cipher)

        test.log.step("9. Load client certificate and server public certificate on module.")
        test.certificates.dstl_upload_openssl_certificates()

        test.log.step("10. Check if certificates are installed")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("11. Set Real Time Clock to current time")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("12. Define PDP context/Internet connection profile for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("13. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("14. Define UDP socket client profile to openSSL server. Use sockudps connection.")
        test.profile = SocketProfile(test.dut, 0, connection_setup.dstl_get_used_cid(), protocol="udp",
                                     host=test.ssl_server.dstl_get_server_ip_address(),
                                     port=test.ssl_server.dstl_get_server_port(), secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(3)

        test.log.step("15. Enable Security Option of IP service (secOpt parameter).")
        test.profile.dstl_set_secopt("1")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())

        test.log.step("16. Save settings of the Internet service profiles.")
        test.expect(dstl_execute_sips_command(test.dut, 'service', 'save'))

        test.log.step("17. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("18. Check if server response is correct.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()
        test.expect(test.ssl_server.dstl_compare_cipher_suite())

        test.log.step("19. Close socket profile.")
        test.log.info("Executed in previous step due to DSTL needing connection to server to be already closed to "
                      "parse server response")

        test.log.step("20. Set new user defined list of available cipher suites on module, choosing a cipher suite "
                      "different than in step 3.")
        chosen_cipher = supported_ciphers[8]
        test.dut.at1.send('at^sbnw="ciphersuites",{}'.format(len(chosen_cipher)))
        test.sleep(3)
        test.dut.at1.send(chosen_cipher, end="")
        test.expect(test.dut.at1.wait_for(".*OK.*"))
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)

        test.log.step("21. Restart module and enter PIN")
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("22. Display current set (user defined list) of cipher suites.")
        test.expect(test.dut.at1.send_and_verify('at^sbnr="ciphersuites","current"', expect=chosen_cipher))
        test.expect(":" not in test.dut.at1.last_response)

        test.log.step("23. Load settings of the Internet service profiles.")
        test.expect(dstl_execute_sips_command(test.dut, 'service', 'load'))

        test.log.step("24. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("25. Open socket profile and check if connection to server has been established")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        if test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared('0')):
            test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id=".*"
                                                                             , urc_info_text=".*error"))

        test.log.step("26. Close socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

        test.log.step("27. Remove certificates from module.")
        test.expect(test.certificates.dstl_delete_all_uploaded_certificates())

        test.log.step("28. Reset and display current list of user defined cipher suites.")
        test.expect(test.dut.at1.send_and_verify('at^sbnw="ciphersuites",0', expect="OK"))
        test.expect(test.dut.at1.send_and_verify('at^sbnr="ciphersuites","current"', expect="No Cipher Suites"))

        test.log.step("29. Restart module")
        test.expect(dstl_restart(test.dut))

    def cleanup(test):
        test.log.step("30. Close OpenSSL server.")
        try:
            test.ssl_server_thread.join()
            test.ssl_server.dstl_server_close_port()
        except AttributeError:
            test.log.info("Object ssl_server does not exist")

        try:
            if test.certificates.dstl_count_uploaded_certificates() is not 0:
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.info("Object certificates does not exist")

        test.dut.at1.send_and_verify('at^sbnw="ciphersuites",0', expect="O")
        test.profile.dstl_get_service().dstl_close_service_profile(expected="O")


if __name__ == "__main__":
    unicorn.main()
