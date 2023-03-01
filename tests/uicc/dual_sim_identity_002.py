#responsible: cong.hu@thalesgroup.com
#location: Dalian
#TC0095565.002
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import check_urc
from dstl.security import lock_unlock_sim

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.log.info('0.0 ############################################################################################################')
        test.log.info('0.0 For VIPER, as the hardware limitation. You need to set the jumper manually before changing the DUALSIM mode.')
        test.log.info('0.0 ############################################################################################################')

        test.log.info('0.1 Set FNS for compatibility.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=GPIO/Mode/FNS,std', expect='.*OK.*'))
        test.log.info('0.2 Set DUALSIM MODE 1.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/DUALMODE,1', expect='.*OK.*'))
        test.log.info('0.3 Restart the module to make the dualmode setting available.')
        test.expect(test.dut.dstl_restart())

        test.log.info('0.4 Disable PIN verification for both (U)SIM cards.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/CS,0', expect='.*OK.*'))
        test.sleep(5)
        test.dut.dstl_unlock_sim()
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/CS,3', expect='.*OK.*'))
        test.sleep(5)
        test.dut.dstl_unlock_sim(test.dut.sim2)

    def run(test):

        imsi_sim1 = test.dut.sim.imsi
        imsi_sim2 = test.dut.sim2.imsi

        test.log.step('1. Set indication of SIM data ready by : at^sset=1')
        test.expect(test.dut.at1.send_and_verify('at^sset=1', expect='.*OK.*'))


        test.log.step('2. Register to network on SIM1')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/CS,0', expect='.*OK.*'))
        test.expect(test.dut.dstl_check_urc('.*\^SSIM READY.*'))
        test.expect(test.dut.dstl_register_to_network())


        test.log.step('3. Enable Dual Mode by: at^scfg="Sim/DualMode","1"')


        test.log.step('4. Switch to SIM2 by: at^scfg="Sim/CS"," 3"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/CS,3', expect='.*OK.*'))

        test.log.step('5. Register to network on SIM2')
        test.expect(test.dut.dstl_check_urc('.*\^SSIM READY.*'))
        test.expect(test.dut.dstl_register_to_network())

        test.log.step('6.Switch between SIM cards and check identity for each (U)SIM cards.')

        for i in range(20):
            if (i % 2 == 0):
                test.log.info(f'This is {i + 1} round of identify checking.')
                test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/CS,0', expect='.*OK.*'))
                test.expect(test.dut.dstl_check_urc('.*\^SSIM READY.*'))
                test.expect(test.dut.dstl_register_to_network())
                test.expect(test.dut.at1.send_and_verify('at+cimi', expect=f'\s+{imsi_sim1}\s+OK.*'))
                test.expect(test.dut.at1.send_and_verify('at+ccid', expect='.*OK.*'))
                test.expect(test.dut.at1.send_and_verify('at+crsm=242', expect='.*OK.*'))
                test.expect(test.dut.at1.send_and_verify('at+cnum', expect='.*OK.*'))
            else:
                test.log.info(f'This is {i + 1} round of identify checking.')
                test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/CS,3', expect='.*OK.*'))
                test.expect(test.dut.dstl_check_urc('.*\^SSIM READY.*'))
                test.expect(test.dut.dstl_register_to_network())
                test.expect(test.dut.at1.send_and_verify('at+cimi', expect=f'\s+{imsi_sim2}\s+OK.*'))
                test.expect(test.dut.at1.send_and_verify('at+ccid', expect='.*OK.*'))
                test.expect(test.dut.at1.send_and_verify('at+crsm=242', expect='.*OK.*'))
                test.expect(test.dut.at1.send_and_verify('at+cnum', expect='.*OK.*'))

        test.log.info('---loop 20 times end---')

        test.log.step('7. Disable Dual Mode by: at^scfg="Sim/DualMode","0"')
        test.log.info('7.1 Lock SIM2.')
        test.dut.dstl_lock_sim(test.dut.sim2)
        test.log.info('7.2 Switch to SIM1.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/CS,0', expect='.*OK.*'))
        test.sleep(5)
        test.log.info('7.3 Lock SIM1.')
        test.dut.dstl_lock_sim()
        test.sleep(5)
        test.log.info('7.4 Disable Dual Mode.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=SIM/DUALMODE,0', expect='.*OK.*'))

    def cleanup(test):
        pass

if '__main__' == __name__:
    unicorn.main()
