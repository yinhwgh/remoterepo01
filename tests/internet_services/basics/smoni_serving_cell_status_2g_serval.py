#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0104291.001

import unicorn
from core.basetest import BaseTest
import time

from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import  dstl_enter_pin
'''Currently,for serval only'''
class Test(BaseTest):
    def setup(test):
        # if test.dut.LTE.lower() == "true":
        #     test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","disabled"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):

        test.log.info('---------Test Begin -------------------------------------------------------------')
        test.log.info('1. Forced "Serching", Limited Service, and "No connection" UE status for 2G network acording with. AT Command Specification document.')
        test.log.info('2. Use AT^SMONI command.')
        test.log.info('3. Compare response with proper section of AT Command Specification document.')
        test.dut.dstl_restart()
        test.check_smoni_response_2g('SEARCH')
        test.expect(test.dut.at1.send_and_verify('at+creg=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sxrat=0', 'OK'))
        test.expect(test.dut.dstl_enter_pin())
        time.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+creg?', 'OK'))
        while '+CREG: 2,1,' not in test.dut.at1.last_response:
            test.check_smoni_response_2g('SEARCH')
            test.expect(test.dut.at1.send_and_verify('at+creg?', 'OK'))
            test.dut.at1.last_response+=test.dut.at1.read()
        time.sleep(5)
        test.check_smoni_response_2g('NOCONN')

        test.log.info('4. Establish data connection and voice call beetwen two modules for 2G network')
        test.log.info('5. Use AT^SMONI command.')
        test.log.info('6. Compare response with proper section of AT Command Specification document.')
        test.establish_data_connection()
        test.check_smoni_response_2g('CONN')
        '''
        test.log.info('!!LIMSRV state need to test manually:unplug antenna '
                      'or insert sim card in arrears')
        test.check_smoni_response_2g('LIMSRV')
        '''
        test.log.info('---------Test End -------------------------------------------------------------')

    def establish_data_connection(test):
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","internet"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sica=1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siss=1,srvtype,socket', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siss=1,conid,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siss=1,address,"socktcp://10.163.27.30:4444"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siso=1', 'OK', wait_for='^SISW: 1,1'))
        test.expect(test.dut.at1.send_and_verify('at^sisw=1,10', '^SISW: 1,10,0'))
        test.dut.at1.send_and_verify('1111111111', wait_for='^SISR: 1,1')

    def check_smoni_response_2g(test,conn_state):
        if conn_state is 'SEARCH':
            test.expect(test.dut.at1.send_and_verify('AT^SMONI', '.*SMONI: Searching'))
        elif conn_state is 'NOCONN':
            #^SMONI: 2G,990,-75,262,03,0139,02C9,28,28,3,0,G,0,-104,NOCONN
            test.expect(
                test.dut.at1.send_and_verify('AT^SMONI',
                                             '.*SMONI: 2G,.*,.*,\d+,\d+,.*,.*,.*,.*,.*,.*,.*,.*,.*,NOCONN'))
        elif conn_state is 'CONN':
            # ^SMONI: ACT,ARFCN,BCCH,MCC,MNC,LAC,cell,C1,C2,NCC,BCC,GPRS,PWR,RXLev,ARFCN,TS,timAdv,dBm,Q,ChMod
            test.expect(
                test.dut.at1.send_and_verify('AT^SMONI',
                                             '.*SMONI: 2G,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*,.*'))
        elif conn_state is 'LIMSRV':
            test.expect(
                test.dut.at1.send_and_verify('AT^SMONI',
                                             '.*SMONI: 2G,.*,.*,\d+,\d+,.*,.*,.*,.*,.*,.*,.*,.*,.*,LIMSRV'))

    def cleanup(test):
        # if test.dut.LTE.lower() == "true":
        #     test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"', ".*OK.*"))
        pass


if "__main__" == __name__:
    unicorn.main()
