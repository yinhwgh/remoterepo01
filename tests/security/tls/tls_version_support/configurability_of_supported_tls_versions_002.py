# responsible marek.kocela@globallogic.com
# Wroclaw
# TC TC0096580.002
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_get_scfg_tcp_tls_version,\
    dstl_set_scfg_tcp_tls_version
from dstl.auxiliary.init import dstl_detect


class Test(BaseTest):
    """To check if supported TLS version is configurable via the AT command (at^scfg)."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):

        test.log.info('TC0096580.002 - ConfigurabilityOfSupportedTLSversions')

        test.log.step('1) Set "MAX" value for "TLS_min_version" and "TLS_max_version" parameters using\n'
                      'AT^SCFG= "Tcp/TLS/Version" write command.')
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MAX", "MAX"))

        test.log.step('2) Using AT^SCFG read command display list of setting and check set values from previous step.')
        test.expect(('MAX', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut))

        test.log.step('3) Try to set all possible values for TLS_min_version parameter using\n'
                      'AT^SCFG= "Tcp/TLS/Version" write command:\n'
                      '- "MIN" automatic minimum\n'
                      '- "1.2" TLSv1.2\n'
                      '- "1.3" TLSv1.3\n'
                      '- "MAX" automatic maximum\n'
                      '- "1.1" TLSv1.1 - set it as a last value')
        tls_min_values = ['MIN', '1.2', '1.3', 'MAX', '1.1']

        for value in tls_min_values:
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, value, 'MAX'))
            test.expect((value, 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut))

        test.log.step('4) Using AT^SCFG read command display list of setting and check if all values from previous\n'
                      'step were set for "Tcp/TLS/Version" (one by one).')
        test.log.info('Done during test step 3')

        test.log.step('5) Try to set all possible values for "TLS_max_version" parameter using\n'
                      'AT^SCFG= "Tcp/TLS/Version" write command:\n'
                      '- "1.2" TLSv1.2\n'
                      '- "1.3" TLSv1.3\n'
                      '- "MAX" automatic maximum')
        tls_max_values = ['1.2', '1.3', 'MAX']

        for value in tls_max_values:
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, '1.1', value))
            test.expect(('1.1', value) == dstl_get_scfg_tcp_tls_version(test.dut))

        test.log.step('6) Using AT^SCFG read command display list of setting and check if all values from previous\n'
                      'step were set for "Tcp/TLS/Version" (one by one)')
        test.log.info('Done during test step 5')

        test.log.step('7) Try to set some illegal values for both parameters')
        illegal_values = {
            'MIN': 'MAX2',
            'MIN2': 'MAX',
            '1.3': '1.1',
            '1.0': '1.3',
            '1.0': '1.4',
            'MIN': 'MAAAAAX',
            '1': '3',
            '@@': 'MAX',
            'MIN': '$$'}

        for min_value, max_value in illegal_values.items():
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, min_value, max_value, expected='.*ERROR.*'))
            test.expect(('1.1', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut))

        test.log.step('8) Repeat step 6')
        test.log.info('Done during test step 7')

        test.log.step('9) Restart module')
        test.expect(dstl_restart(test.dut))

        test.log.step('10) Repeat step 6')
        test.expect(('1.1', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut))

    def cleanup(test):
        test.log.info('Restoring default values of TLS versions')
        dstl_set_scfg_tcp_tls_version(test.dut, '1.2', 'MAX')


if "__main__" == __name__:
    unicorn.main()