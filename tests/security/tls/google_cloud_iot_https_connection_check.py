# responsible maciej.gorny@globallogic.com
# location: Wroclaw
# TC0105436.001
from os.path import join
import unicorn
from core.basetest import BaseTest
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.security.internet_service_signature import InternetServiceSignatures
from dstl.status_control.extended_indicator_control import dstl_enable_one_indicator


class Test(BaseTest):
    """Checking secure connection to HTTPs service on Google cloud IoT - with and without
    certificate check on module."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

        test.preloaded_cert = InternetServicesCertificates(test.dut, mode="preconfig_cert")
        test.is_cert = InternetServicesCertificates(test.dut)

        test.cert_file = join(test.preloaded_cert.certificates_path, "openssl_certificates",
                              "client.der")
        test.key_file = join(test.preloaded_cert.certificates_path, "openssl_certificates",
                             "private_client_key")
        if not test.is_cert.dstl_count_uploaded_certificates() == 0:
            test.preloaded_cert.dstl_delete_all_certificates_using_ssecua()
        test.expect(test.is_cert.dstl_count_uploaded_certificates() == 0,
                    msg="Problem with deleting certificates from module")
        test.preloaded_cert.dstl_upload_certificate_at_index_0(test.cert_file, test.key_file)
        preloaded_certs_update = InternetServiceSignatures(test.dut)
        preloaded_certs_update.dstl_initialize_is_store_non_security_mode()
        test.expect(test.is_cert.dstl_count_uploaded_certificates() > 10,
                    msg="Problem with certificates initialization from preconfig store")

    def run(test):
        test.log.info("Executing script for test case: "
                      "'TC0105436.001 GooglecloudIoTHttpsConnectionCheck'")

        supported_host = ["good.gsr2demo.pki.goog", "good.r3demo.pki.goog",
                          "good.r4demo.pki.goog", "good.r1demo.pki.goog",
                          "good.r2demo.pki.goog", "good.r4demo.pki.goog", "good.r3demo.pki.goog",
                          "good.gsr4demo.pki.goog", "good.gsr2demo.pki.goog", "www.ipko.pl"]
        test.https_profiles = []
        test.package_to_read = 1500

        test.log.step("1. Attach DUT to the network")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Define and activate PDP context / connection Profile")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.con_id = connection_setup.dstl_get_used_cid()

        for sec_opt in range(2):
            test.log.info(sec_opt)

            test.log.step("3. Define HTTPs get profile on all profiles "
                          "(set secopt parameter to {})".format(sec_opt))
            for srv_id in range(10):
                test.https_profiles.append(test.define_https_profiles(srv_id,
                                                                      supported_host[srv_id],
                                                                      sec_opt))
            test.expect(dstl_get_siss_read_response(test.dut))

            test.log.step("4. Enable sind is_cert URC")
            test.expect(dstl_enable_one_indicator(test.dut, "is_cert"))

            for srv_id in range(3):
                test.steps_5_6(srv_id)
                test.steps_5_6(srv_id+3)
                test.steps_5_6(srv_id+6)
                test.steps_7_8(srv_id)
                test.steps_7_8(srv_id+3)
                test.steps_7_8(srv_id+6)

            test.log.step("9. Set secopt parameter to 1 and repeat steps 3-8")

        test.log.step("10. Define connection to e.g. some different site and check if "
                      "it's possible (with secopt1)")
        test.log.info("Connection defined in step 3")
        test.expect(test.https_profiles[9].dstl_get_service().
                    dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.https_profiles[9].dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0",
                                                        urc_info_id="76",
                                                        urc_info_text='"Certificate format error"'))
        test.expect(test.https_profiles[9].dstl_get_service().dstl_read_data(test.package_to_read))
        test.expect(test.https_profiles[9].dstl_get_service().
                    dstl_close_service_profile())

    def cleanup(test):
        try:
            test.expect(test.preloaded_cert.dstl_delete_certificate(0))
            test.expect(test.is_cert.dstl_delete_all_certificates_using_ssecua())
            test.expect(test.is_cert.dstl_count_uploaded_certificates() == 0,
                        msg="Problem with deleting certificates from module")
        except AttributeError:
            test.log.error("Certificate object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def define_https_profiles(test, srv_id, supported_host, sec_opt):
        test.https_client = HttpProfile(test.dut, srv_id, test.con_id, http_command="get",
                                   host=supported_host, secure_connection=True,
                                   secopt="{}".format(sec_opt))
        test.https_client.dstl_generate_address()
        test.expect(test.https_client.dstl_get_service().dstl_load_profile())
        return test.https_client

    def steps_5_6(test, srv_id):
        test.log.step("5. Open and establish HTTPs connection (open more than 8 profiles "
                      "at the same time - for some products like Serval it could be limited"
                      " to 2 due the memory limitations)")
        test.expect(test.https_profiles[srv_id].dstl_get_service().
                    dstl_open_service_profile())
        test.expect(test.https_profiles[srv_id].dstl_get_urc().
                    dstl_is_sisr_urc_appeared(1))
        test.expect("CIEV: is_cert," in test.dut.at1.last_response)

        test.log.step("6. Check URC shows that data can be read")
        test.log.info("Done in previous step")

    def steps_7_8(test, srv_id):
        test.log.step("7. Read all data from server")
        test.expect(test.https_profiles[srv_id].dstl_get_service().dstl_read_all_data
                    (test.package_to_read))

        test.log.step("8. Close connection")
        test.expect(test.https_profiles[srv_id].dstl_get_service().
                    dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
