#responsible maciej.gorny@globallogic.com
#location: Wroclaw
#TC0104224.001 TlsVersionOnDifferentInterfaces
import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_tls_version import *
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect

class Test(BaseTest):
    """
        Short description:
        To check if the TLS version cannot be set to different values on different interfaces
        simultaneously (cover of IPIS100275018).

        Detailed description:
        Set parameter "Tcp/TLS/Version" to different values on every interface (if product support more than one) e.g.:
        1. Set at^scfg="Tcp/TLS/Version","1.2","MAX" on ASC0 interface.
        2. Set at^scfg="Tcp/TLS/Version","1.1","MAX" on USB1 / ASC1 interface.
        3. Set at^scfg="Tcp/TLS/Version","MIN","MAX" on MDM interface (if supported).
        4. Check value of at^scfg="Tcp/TLS/Version" on every interface.
       """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):
        test.log.h2("Executing script for test case: TC0104224.001 TlsVersionOnDifferentInterfaces ")

        test.log.step("1) Set at^scfg='Tcp/TLS/Version','1.2','MAX' on ASC0 interface.")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "1.2", "MAX",))

        test.log.step("2) Set at^scfg='Tcp/TLS/Version','1.1','MAX' on USB1 / ASC1 interface.")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "1.1", "MAX", device_interface="at2"))

        test.log.step("3) Set at^scfg='Tcp/TLS/Version','MIN','MAX'' on MDM interface (if supported).")
        if test.dut.project is 'VIPER':
            test.log.info("According to the standard TIM configuration for Viper only "
                          "ASC0 and ASC1 interfaces are supported")
        if test.dut.project is 'SERVAL':
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX", device_interface="at3"))

        test.log.step("4) Check value of at^scfg='Tcp/TLS/Version' on every interface.")
        if test.dut.project is 'VIPER':
            test.expect(('1.1', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut))
            test.expect(('1.1', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut, device_interface="at2"))
        if test.dut.project is 'SERVAL':
            test.expect(('MIN', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut))
            test.expect(('MIN', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut, device_interface="at2"))
            test.expect(('MIN', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut, device_interface="at3"))

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))


if "__main__" == __name__:
    unicorn.main()
