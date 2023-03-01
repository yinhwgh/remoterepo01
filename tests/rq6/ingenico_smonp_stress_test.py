# responsible:dan.liu@thalesgroup.com
# location: Dalian
# TC0108067.001

import unicorn
from core.basetest import BaseTest
from dstl.packet_domain import start_public_IPv4_data_connection
from dstl.packet_domain.start_public_IPv4_data_connection import get_ip_address_windows
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network

class Test(BaseTest):
    """
        TC0108067.001 - Ingenico_SMONPStressTest
        at1: dAsc0
        at2: Modem
        Please set up a dial up connection named "lynx"  on your pc before run this script
    """

    def setup(test):
        dstl_detect(test.dut)
        test.dialup_conn_name = 'lynx'

    def run(test):
        test.log.step("1. Enter sim pin. Make module into sleep mode.")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('AT^SPOW=2,1000,3'))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('ATE0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGMM', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGMR', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGSN', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('ATI1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT&W', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/CS"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CRSM=176,12258,0,0,10', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CLCK="SC",2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGREG=0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=3,2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=0,0,0,0,1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMGF=0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CRSM=176,28486,0,0,17', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CNUM', ".*OK.*"))

        test.log.step("2. Register on Network")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("3. Establish dial-up connection ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple
                    (test, "at2", test.dialup_conn_name), critical=True)
        test.at_thread=test.thread(test.send_atc, test.dut.at1)
        test.at_thread.join()

    def cleanup(test):
        test.log.step("5. Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)


    def send_atc(test, port):
        test.log.step("4. Send following at commands 1000 loops")
        for i in range(1, 500):
            test.log.info('this is loop {}'.format(i))
            test.expect(port.send_and_verify('at+cgatt?', 'OK'))
            test.expect(port.send_and_verify('at+cgdcont?', 'OK'))
            test.expect(port.send_and_verify('at+cgpaddr=1', 'OK'))
            test.expect(port.send_and_verify('at+ceer', 'OK'))
            test.expect(port.send_and_verify('AT+COPS?', 'OK'))
            test.expect(port.send_and_verify('AT+CGDCONT=1,"IP","CUGONEE.TELUS.COM",,0,0', ".*OK.*"))
            test.expect(port.send_and_verify('AT+CGDCONT?', 'OK'))
            test.expect(port.send_and_verify('AT^SXRAT?', 'OK'))
            test.expect(port.send_and_verify('at^sind=service,0', 'OK'))
            test.expect(port.send_and_verify('AT^SIND=call,0', 'OK'))
            test.expect(port.send_and_verify('AT^SIND=message,0', 'OK'))
            test.expect(port.send_and_verify('AT+CSQ', 'OK'))
            test.expect(port.send_and_verify('AT+CREG?', 'OK'))
            test.expect(port.send_and_verify('AT+CGREG?', 'OK'))
            test.expect(port.send_and_verify('AT+CEREG?', 'OK'))
            test.expect(port.send_and_verify('AT^SMONI', 'OK'))
            test.expect(port.send_and_verify('AT^SMONP', 'OK'))
            test.expect(port.send_and_verify('at+cgpaddr=1', 'OK'))
            pdp_address = test.dut.at1.last_response.split("\r\n")[1].split(",")[1].replace('\"', '')
            print(pdp_address)
            pdp_address_list=[]
            for i in range(1, 5):
                temp = pdp_address.split('.')[i-1]
                pdp_address_list.append(temp)
            windows_address = get_ip_address_windows()
            print(windows_address)
            windows_address_list = []
            for i in range(1, 5):
                temp = pdp_address.split('.')[i - 1]
                windows_address_list.append(temp)
            for i in range(1, 5):
                if pdp_address_list[i-1] == windows_address_list[i-1]:
                    test.expect(True)
                    test.log.info('PPP connection keeps well ')
                else:
                    test.expect(False, critical=True)
                    test.log.info('PPP  disconnect')

if (__name__ == "__main__"):
    unicorn.main()
