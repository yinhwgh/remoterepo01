#author: cong.hu@thalesgroup.com
#location: Dalian
#TC0095574.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT+CREG=1', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', expect='.*OK.*'))
        test.expect(test.dut.at2.send_and_verify('AT+CREG=1', expect='.*OK.*'))
        test.expect(test.dut.at2.send_and_verify('AT+CMEE=2', expect='.*OK.*'))

    def run(test):
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\s+\+CPIN: SIM PIN\s+OK.*'))
        test.log.info('1.Enable Dual Mode by AT^SCFG="SIM/DualMode","1"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/DualMode","1"', expect='.*OK.*'))

        test.log.info('2.Enter SIM PIN1 for sim card 1.')
        test.expect(test.dut.dstl_enter_pin())

        test.log.info('3.Wait for the module registers to the network.')
        test.expect(test.dut.dstl_check_urc('\s+\+CREG: 1\s+OK.*'))

        test.log.info('4. Switch to SIM2.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Sim/CS","3"', expect='.*OK.*'))

        test.log.info('5.Enter SIM PIN1 for sim card 2.')
        test.expect(test.dut.dstl_enter_pin())

        test.log.info('6.Wait for the module registers to the network.')
        test.expect(test.dut.dstl_check_urc('\s+\+CREG: 1\s+OK.*'))

        test.log.info('7.Setup Internet Connection Profile.')
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=6,"IPV4V6","internet"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,6', expect='.*OK.*'))

        test.log.info('8.Setup Internet Service Profile(FTP PUT session). Here, the address is the IPV4 address for CMW500 located in Dalian Mini lab.')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"srvtype","ftp"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"conId",6', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"address","ftp://10.0.1.15:21/cohu_test.txt"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"cmd",","put"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"user","test"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"passwd","test"', expect='.*OK.*'))

        test.log.info('9.Open the Service.')
        test.expect(test.dut.at1.send_and_verify('AT^SISO=1', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('.*\^SISW: 1,1.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISW=1,10', expect='\s+\^SISW: 1,10,0\s+OK/*'))
        test.expect(test.dut.at1.send_and_verify('1234567890', expect='\s+\^SISW: 1,1.*'))

        test.log.info('10.Send some data(without EOD).')
        test.expect(test.dut.at1.send_and_verify('AT^SISW=1,10', expect='\s+\^SISW: 1,10,0\s+OK/*'))

        test.log.info('11.Switch SIM.')
        test.expect(test.dut.at2.send_and_verify('AT^SCFG="Sim/CS","1"', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('\s+\+CREG: 1\s+OK.*'))

        test.log.info('12.Close the profile.')
        test.expect(test.dut.at1.send_and_verify('AT^SISC=1', expect='.*OK.*'))

        test.log.info('13.Setup Internet Service Profile(FTP GET session).')
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,6', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"cmd",","get"', expect='.*OK.*'))

        test.log.info('14.Open the service.')
        test.expect(test.dut.at1.send_and_verify('AT^SISO=1', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('.*\^SISR: 1,1.*'))

        test.log.info('15.Read data (not all).')
        test.expect(test.dut.at1.send_and_verify('at^sisr=1,5', expect='.*OK.*'))

        test.log.info('16.Switch SIM.')
        test.expect(test.dut.at2.send_and_verify('AT^SCFG="Sim/CS","3"', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('\s+\+CREG: 1\s+OK.*'))

        test.log.info('17.Read rest data.')
        test.expect(test.dut.at1.send_and_verify('at^sisr=1,5', expect='.*OK.*'))

        test.log.info('18.Close the profile.')
        test.expect(test.dut.at1.send_and_verify('AT^SISC=1', expect='.*OK.*'))

        test.log.info('19.Delete the profile.')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"SRVTYPE","none"', expect='.*OK.*'))

        test.log.info('Repeat step 7 to step 19 using SIM1 instead of SIM2.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Sim/CS","1"', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('\s+\+CREG: 1\s+OK.*'))

        test.log.info('20.Setup Internet Connection Profile.')
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,6', expect='.*OK.*'))

        test.log.info('21.Setup Internet Service Profile(FTP PUT session). Here, the address is the IPV4 address for CMW500 located in Dalian Mini lab.')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"srvtype","ftp"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"conId",6', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"address","ftp://10.0.1.15:21/cohu_test.txt"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"cmd",","put"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"user","test"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"passwd","test"', expect='.*OK.*'))

        test.log.info('22.Open the Service.')
        test.expect(test.dut.at1.send_and_verify('AT^SISO=1', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('.*\^SISW: 1,1.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISW=1,10', expect='\s+\^SISW: 1,10,0\s+OK/*'))
        test.expect(test.dut.at1.send_and_verify('1234567890', expect='\s+\^SISW: 1,1.*'))

        test.log.info('23.Send some data(without EOD).')
        test.expect(test.dut.at1.send_and_verify('AT^SISW=1,10', expect='\s+\^SISW: 1,10,0\s+OK/*'))

        test.log.info('24.Switch SIM.')
        test.expect(test.dut.at2.send_and_verify('AT^SCFG="Sim/CS","3"', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('\s+\+CREG: 1\s+OK.*'))

        test.log.info('25.Close the profile.')
        test.expect(test.dut.at1.send_and_verify('AT^SISC=1', expect='.*OK.*'))

        test.log.info('26.Setup Internet Service Profile(FTP GET session).')
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,6', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"cmd",","get"', expect='.*OK.*'))

        test.log.info('28.Open the Service.')
        test.expect(test.dut.at1.send_and_verify('AT^SISO=1', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('.*\^SISR: 1,1.*'))

        test.log.info('29.Read data (not all).')
        test.expect(test.dut.at1.send_and_verify('at^sisr=1,5', expect='.*OK.*'))

        test.log.info('30.Switch SIM.')
        test.expect(test.dut.at2.send_and_verify('AT^SCFG="Sim/CS","1"', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('\s+\+CREG: 1\s+OK.*'))

        test.log.info('31.Read rest data.')
        test.expect(test.dut.at1.send_and_verify('at^sisr=1,5', expect='.*OK.*'))

        test.log.info('32.Close the profile.')
        test.expect(test.dut.at1.send_and_verify('AT^SISC=1', expect='.*OK.*'))

        test.log.info('33.Delete the profile.')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"SRVTYPE","none"', expect='.*OK.*'))

    def cleanup(test):
        test.expect(test.dut.dstl_restart())

if '__main__' == __name__:
    unicorn.main()
