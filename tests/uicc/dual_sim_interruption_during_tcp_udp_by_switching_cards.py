#author: yandong.wu@thalesgroup.com
#location: Dalian
#TC0092008.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+creg=1', 'OK'))

    def run(test):
        test.log.info('1.Enable Dual Mode by AT^SCFG="SIM/DualMode","1"')
        test.expect(test.dut.at1.send_and_verify('at^scfg="GPIO/mode/FNS","std"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="SIM/DualMode","1"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Sim/CS","0"', 'OK'))
        test.sleep(10)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())

        test.log.info('2.Switch SIM.')
        test.expect(test.dut.at1.send_and_verify('at^scfg="Sim/CS","3"', 'OK'))
        test.sleep(10)
        test.log.info('3.Enter PIN1 for sim')
        test.expect(test.dut.dstl_enter_pin())
        #test.sleep(5)
        test.log.info('4.Register to the network.')
        test.expect(test.dut.dstl_register_to_network())


        test.log.info('4.Create an Internet connection profile')
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,3', 'OK'))

        test.log.info('5.Setup Internet Service Profile (TCP)')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"srvType","Socket"', 'OK'))
        #test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"conId","1"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"conId","3"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"address","socktcp://182.92.198.110:9011"', 'OK'))
        #test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"address","sockudp://182.92.198.110:9010"', 'OK'))

        test.log.info('6.Open the Service Profile')
        test.expect(test.dut.at1.send_and_verify('AT^SISO=1', 'OK'))
        #test.expect(test.dut.dstl_check_urc('.*\^SISW: 1,1'))
        test.log.info('7.Send the data')
        #test.expect(test.dut.at1.send_and_verify('AT^SISW=1,10', 'OK'))
        #test.expect(test.dut.at1.send_and_verify('AT^SISW=1,10'))
        test.expect(test.dut.at1.send_and_verify('AT^SISW=1,10', expect='\s+\^SISW: 1,10,0\s+OK/*'))
        #test.expect(test.dut.at1.send_and_verify('1234567890', expect='\s+\^SISW: 1,1.*'))
        test.expect(test.dut.at1.send_and_verify('1234567890', 'OK'))
        test.expect(test.dut.dstl_check_urc('.*\^SISW: 1,1'))
        test.expect(test.dut.dstl_check_urc('.*\^SISR: 1,1'))

        test.log.info('8.Read a part of the data')
        test.expect(test.dut.at1.send_and_verify('AT^SISR=1,5', 'OK'))
        #12345
        test.log.info('9.Switch SIM.')
        test.expect(test.dut.at1.send_and_verify('at^scfg="Sim/CS","0"', 'OK'))
        test.sleep(10)
        test.log.info('10.Enter PIN1 for sim')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.log.info('11.Register to the network.')
        test.expect(test.dut.dstl_register_to_network())

        test.log.info('12.Read the rest of the data')
        test.expect(test.dut.at1.send_and_verify('AT^SISR=1,5', 'OK'))
        #67890








        test.log.info('13.Close the profile.')
        test.expect(test.dut.at1.send_and_verify('AT^SISC=1', 'OK'))





    def cleanup(test):
        pass


if '__main__' == __name__:
    unicorn.main()
