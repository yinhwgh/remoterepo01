#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC TC0088105.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        # restrart
        test.dut.dstl_restart()
        test.sleep(10)

    def run(test):

        test.log.info('1.PIN lock disabled')
        test.dut.dstl_unlock_sim()

        test.log.info('1.1 Set AutoAttach to enabled, restart module by at+cfun=1,1, check attach.')
        setandcheck_autoattach(test,'enabled')
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_register_to_network()
        test.sleep(15)
        check_attach_status(test,'1')

        test.log.info('1.2 Set AutoAttach to disabled, restart module by at+cfun=1,1, check attach.'
                      'Send AT+CGATT=1 then check attach.')
        setandcheck_autoattach(test, 'disabled')
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.at1.send_and_verify('at+cpin?',expect='READY')
        test.sleep(15)
        check_attach_status(test,'0')

        test.log.info('2.PIN lock enabled')
        test.dut.dstl_lock_sim()

        test.log.info('2.1 Set AutoAttach to enabled, restart module by at+cfun=1,1, verify PIN, check attach')
        setandcheck_autoattach(test, 'enabled')
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_register_to_network()
        test.sleep(15)
        check_attach_status(test,'1')

        test.log.info('2.2 Set AutoAttach to disabled, restart module by at+cfun=1,1, verify PIN, check attach. '
                      'Send AT+CGATT=1 then check attach.')
        setandcheck_autoattach(test, 'disabled')
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_register_to_network()
        test.sleep(15)
        check_attach_status(test,'0')

        test.log.info('3.1 Set AutoAttach to disabled, check it is not changed by AT&F. '
                      'Restart module by at+cfun=1,1, check that AutoAttach setting is not changed by AT&F.')
        setandcheck_autoattach(test, 'disabled')
        test.dut.at1.send_and_verify('at&f')
        check_autoattach(test,'disabled')
        test.dut.dstl_restart()
        test.sleep(5)
        check_autoattach(test, 'disabled')

        test.log.info('3.2 Set AutoAttach to enabled, check it is not changed by AT&F. '
                      'Restart module by at+cfun=1,1, check that AutoAttach setting is not changed by AT&F.')
        setandcheck_autoattach(test, 'enabled')
        test.dut.at1.send_and_verify('at&f')
        check_autoattach(test, 'enabled')
        test.dut.dstl_restart()
        test.sleep(5)
        check_autoattach(test, 'enabled')

        test.log.info('4.Set AutoAttach to disabled, reset factory default, restart module by at+cfun=1,1.'
                      'Verify autoattach setting, verify PIN, check attach')
        if (test.dut.product == 'cougar') :
            setandcheck_autoattach(test, 'disabled')
            test.dut.at1.send_and_verify('at^scfg=\"MEopMode/Factory\",\"all\"', wait_for='.*SYSSTART.*')
            test.dut.restart()
            test.sleep(5)
            check_autoattach(test, 'enabled')
            test.dut.register_to_network()
            test.sleep(15)
            check_attach_status(test,'1')
        else:
            test.log.info(test.dut.product+' does not support this feature, test step skipped')

    def cleanup(test):
        pass


def setandcheck_autoattach(test,status):
    test.dut.at1.send_and_verify('at^scfg=\"GPRS/AutoAttach\",\"{}\"'.format(status))
    test.expect(test.dut.at1.send_and_verify('at^scfg=\"GPRS/AutoAttach\"',expect='\"GPRS/AutoAttach\",\"{}\"'.format(status)))

def check_autoattach(test,status):
    test.expect(test.dut.at1.send_and_verify('at^scfg=\"GPRS/AutoAttach\"', expect='\"GPRS/AutoAttach\",\"{}\"'.format(status)))

def check_attach_status(test,status):
    test.expect(test.dut.at1.send_and_verify('at+cgatt?', expect='CGATT: '+status))

if "__main__" == __name__:
    unicorn.main()
