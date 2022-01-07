# responsible hongwei.yin@thalesgroup.com
# location Dalian
# TC0107792.001 according to RQ6000061.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import\
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
import resmed_ehealth_initmodule_normal_flow


class Test(BaseTest):
    """
       TC0107792.001 - Resmed_eHealth_DisableFlightMode_NormalFlow
    """

    def setup(test):
        test.expect(test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK'))
        test.sleep(1.5)

    def run(test):
        test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 1))

    def cleanup(test):
        pass

if __name__ == "__main__":
    unicorn.main()