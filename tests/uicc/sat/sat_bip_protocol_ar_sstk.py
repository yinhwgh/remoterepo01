#responsible  yanen.wang@thalesgroup.com
#location: Beijing
#TC0104182.001

import unicorn
import socket

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_register_to_network

class Test(BaseTest):
    """
       TC0104182.001 -	TpSATBipProtocol_AR_SSTK
       Debugged: Viper
       Need the specified SIM
    """

    def setup(test):
        dstl_detect(test.dut)
        test.log.info("Setting AR mode on Remote-SAT interface")
        test.dut.at1.send_and_verify('AT^SSTA=0', 'OK')
        test.log.info("Restart the module ")
        dstl_restart(test.dut)
        test.log.info("Setting error format")
        test.dut.at1.send_and_verify(' AT+CMEE=2','OK')
        test.log.info("Enabling SAT SSTK URCs")
        test.dut.at1.send_and_verify('AT^SCFG="SAT/URC",1', 'OK')
        test.dut.at1.send_and_verify('AT+CEREG=2', 'OK')
        dstl_register_to_network(test.dut)

    def run(test):
        packed_ip_addr = socket.inet_aton(test.ftp_server_ipv4)
        hexStr = packed_ip_addr.hex().upper()
        test.log.step("1. Trigger execution of OPEN_CHANNEL*")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D02F8103014003820281820500350702020403051F0239020578470908696E7465726E65743C0302115C3E0521{}"'.format(hexStr),
                                                 r'(.*SSTK: "D02F8103014003820281820500350702020403051F0239020578470908696E7465726E65743C0302115C3E0521{}")'.format(hexStr),
                                                wait_for='.*SSTK: "810301400[1|3][0|8]2028281[0|8]30100[3|B]8028100[3|B]5070202040[3|5]051F02[3|B]9020578"',timeout=60))
        test.log.step("2. Trigger execution of SEND_DATA*")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D013810301430182028121B6083132333435363738"',
                                                 '.*SSTK: "D013810301430182028121B6083132333435363738",21,"00".*SSTK: "8103014301[0|8]2028281[0|8]30100[3|B]701FF",15,"01"',
                                                 wait_for='.*SSTK: "D60E[1|9]90109[0|8]2028281[3|B]8028100[3|B]70108",16,"03".*',timeout=60))

        test.log.step("3. Trigger execution of RECEIVE_DATA")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D00C810301420082028121B70108"',
                                                 '.*\^SSTK: "D00C810301420082028121B70108",14,"00".*SSTK: "8103014200[0|8]2028281[0|8]30100[3|B]6083132333435363738[3|B]70100",25,"01".*'))

        test.log.step("4. Trigger execution of GET_CHANNEL_STATUS")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301440082028182"',
                                                 '.*\^SSTK: "D009810301440082028182",11,"00".*SSTK: "8103014400[0|8]2028281[0|8]30100[3|B]8028100[3|B]8020200[3|B]8020300[3|B]8020400[3|B]8020500[3|B]8020600[3|B]8020700",40,"01".*'))

        test.log.step("5. Trigger execution of CLOSE_CHANNEL")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301410082028121"',
                                                 '.*SSTK: "D009810301410082028121",11,"00".*SSTK: "8103014100[0|8]2028281[0|8]30100",12,"01".*',
                                                 wait_for='"8103014100[0|8]2028281[0|8]30100",12',timeout=60))
        test.log.info("**** TEST End ****")
    def cleanup(test):
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass


if (__name__ == "__main__"):
    unicorn.main()
