# responsible: yi.guo@thalesgroup.com
# location: Beijing
# TC0107080.002 -  Multi_MNO_Configurations_Manual_Selection_Basic

'''
Test with McTest4 board
Dut is Serval



'''

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.configuration.configure_scfg_provider_profile import *
from dstl.auxiliary import restart_module

class MNO_Manual_Select(BaseTest):
    provlist = ["fallb3gpp", "telstraau", "Commercial-SKT", "attus", "verizonus"]
    unsupport_provlist = ["tmode","vdfde","cmcc","3gpp"]

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_switch_on_provider_auto_select()


    def run(test):
        test.log.step('1. Check the supported parameters list of "MEopMode/Prov/Cfg" via "AT^SCFG=?"')
        current_prov_list = test.dut.dstl_read_all_supported_provider_profile_configs()
        test.log.info("Current prov list is {}".format(current_prov_list))
        test.expect(current_prov_list.sort() == test.provlist.sort())

        test.log.step('2.Check current parameters of "MEopMode/Prov/Cfg"')
        current_prov = test.dut.dstl_read_provider_profile_config()
        current_prov_list.remove(current_prov)

        test.log.step('3.Try to change "MEopMode/Prov/Cfg" to other supported value')
        for prov_name in current_prov_list:
            test.expect(not test.dut.dstl_select_provider_profile_config(prov_name))

        test.log.step('4.Change "MEopMode/Prov/AutoSelect" to "off", then restart module')
        test.dut.dstl_switch_off_provider_auto_select()
        test.dut.dstl_restart()

        test.log.step('5.Change "MEopMode/Prov/Cfg" to other supported values.')
        current_prov_list.append(current_prov)
        for prov_name in current_prov_list:
            test.expect(test.dut.dstl_select_provider_profile_config(prov_name))
            if current_prov == prov_name:
                test.expect(test.dut.at1.wait_for('+CIEV: prov,0,"{}"'.format(current_prov), append=True,timeout=10))
            else:
                test.expect(test.dut.at1.wait_for('+CIEV: prov,1,"{}","{}"'.format(prov_name,current_prov), append=True,timeout=10))

        test.log.step('6.Try to Change "MEopMode/Prov/Cfg" to other not-supported values, like , "tmode","vdfde","cmcc","3gpd" etc.')
        for prov_name in test.unsupport_provlist:
            test.expect(test.dut.at1.send_and_verify(F'AT^SCFG="MEopMode/Prov/Cfg","{prov_name}"', 'ERROR|error'))

    def cleanup(test):
        test.dut.dstl_switch_on_provider_auto_select()
        test.dut.dstl_restart()


if (__name__ == "__main__"):
    unicorn.main()
