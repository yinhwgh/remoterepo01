# responsible: jingxin.shen@thalesgroup.com
# location: Beijing

import unicorn
import re
import time
from core.basetest import BaseTest
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.usim import get_imsi
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import check_urc
from dstl.auxiliary.restart_module import dstl_restart
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.network_service.register_to_network import *
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary.devboard.devboard import *
from dstl.packet_domain import start_public_IPv4_data_connection

import json
import datetime

def setup_for_provision_or_swich(test):
    test.rest_client = IotSuiteRESTClient()
    dstl.require_parameter('unicorn_step_version', default='unicorn_step_2')
    dstl.require_parameter('rat', default='cat_nb')
    dstl.require_parameter('cmw500_network', default='False')
    dstl.require_parameter('dialup_start', default='False')
    dstl.require_parameter('fallback_test', default='False')
    test.log.step('[Setup]-1.Product detection.')
    test.dut.dstl_detect()
    test.log.step('[Setup]-2.Configure mask of CIoT capability for SRV03-3217.')
    config_mask_of_CIoT_capability(test)
    test.log.step('[Setup]-3.Set connection interval to 24h.')
    set_modes_register_update_time(test)
    test.log.step("[Setup]-4.Set real time clock.")
    test.dut.dstl_set_real_time_clock()
    test.log.step("[Setup]-5.Disable eDRX.")
    disable_edrx(test)
    test.log.step("[Setup]-6.Enable urc of temperature monitoring.")
    test.dut.at1.send_and_verify('at^sctm=1,1', 'OK')
    test.log.step("[Setup]-7.Check if device exists if no create device.")
    imei = test.dut.dstl_get_imei()
    test.log.info("This is your IMEI: " + imei)
    devices = get_devices().json()
    device_id = get_device_id(devices, imei)
    if not device_id:
        test.log.info("Create device with your imei.")
        label = test.dut.dstl_get_device_label()
        response = create_device(imei, label)
        log_body(response)
    test.log.step("[Setup]-8.Update mods url,due to IP address can not work from SW048F.")#SRV03-4975
    test.dut.at1.send_and_verify('at^srvcfg=MODS,address,coaps://partners-dgw.iot-suite.thalescloud.io:5684','OK')
    test.log.step("[Setup]-9.Setting RS profile iccid in susmc.")
    test.dut.at1.send_and_verify('at^susma?', wait_for="OK", timeout=10)
    rs_iccid_susma = re.search('\^SUSMA: "LPA/Profiles/Info",1,[01],"(\d+)",.*', test.dut.at1.last_response).group(1)
    test.dut.dstl_activate_cm_hidden_commands()
    test.dut.at1.send_and_verify(f'at^susmc="ConMgr/Profile/Table",1,"{rs_iccid_susma}","R&S",1,1,"internet","","",0,0')
    test.dut.dstl_activate_cm_hidden_commands()
    test.log.step("[Setup]-10.Setting band for CMCC cat-nb network in China.")
    setting_band_cmcc_nb(test)
    return

def setting_band_cmcc_nb(test):
    if test.cmw500_network is True or test.fallback_test is True:
        test.expect(
            test.dut.at1.send_and_verify('at^scfg="Radio/Band/CatM","0f0e189f","0010000200000000"', expect='.*OK.*'))
        test.expect(
            test.dut.at1.send_and_verify('at^scfg="Radio/Band/CatNB","0b0e189f","0010004200000000"', expect='.*OK.*'))
        test.dut.dstl_restart()
        if test.cmw500_network is True:
            test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60)
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Band/CatM"',
                                                 expect='\^SCFG: "Radio/Band/CatM","0f0e189f","0010000200000000".*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Band/CatNB"',
                                                 expect='\^SCFG: "Radio/Band/CatNB","0b0e189f","0010004200000000".*OK.*'))
    else:
        test.expect(test.dut.at1.send_and_verify('at^sxrat=8,8', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Band/CatM","00000000"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Band/CatNB","00000080"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Band/Opt/Ctrl",0', expect='.*OK.*'))
        test.dut.dstl_restart()
        test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"', timeout=10)
        test.expect(
            test.dut.at1.send_and_verify('at^sxrat?', expect='\^SXRAT: 8, 8.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Band/CatM"',
                                                 expect='\^SCFG: "Radio/Band/CatM","00000000".*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Band/CatNB"',
                                                 expect='\^SCFG: "Radio/Band/CatNB","00000080".*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Band/Opt/Ctrl"',
                                                 expect='\^SCFG: "Radio/Band/Opt/Ctrl","0".*OK.*'))
    return

def connectivity_provision_module_configure(test,step):
    test.require_parameter('profile_number_before_download', default=2)
    test.log.step(f'{step}.1:Check apn.')
    test.expect(test.dut.at1.send_and_verify('at+cops?', expect='.*OK.*'))
    if "+CME ERROR: SIM busy" in test.dut.at1.last_response:
        test.expect(False,msg='SIM busy issue of bootstrap happened.')
        test.log.com('++++ WORKAROUND_SIM_BUSY - Start *****')
        test.dut.dstl_restart()
        if test.cmw500_network is True:
            test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60)
        else:
            test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"', timeout=10)
        test.log.com('++++ WORKAROUND_SIM_BUSY - End *****')
    test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))
    last_response = test.dut.at1.last_response
    if "JTM2M" in last_response:
        test.log.info("APN which you are looking occurs in response")
    else:
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","JTM2M"', expect='.*OK.*'))
    test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS', expect='.*OK.*')
    last_response = test.dut.at1.last_response
    if '"APN_NAME","JTM2M"' in last_response and '"APN","JTM2M"' in last_response:
        test.log.info("APN which you are looking occurs in response")
    else:
        test.log.info("Required APN not found, test will be terminated")
        return False
    test.log.step(f'{step}.2:Init all mods settings.')
    test.expect(test.dut.dstl_init_all_mods_settings())
    test.log.step(f'{step}.3:Set Provisioning Rule ID')
    test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",UNICORN-POC', expect='.*OK.*'))
    test.log.step(f'{step}.4:Set Download Mode to 1')
    test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*'))
    test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode"', expect='.*OK.*'))
    if test.unicorn_step_version == 'unicorn_step_2':
        test.log.step(f'{step}.5:Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr will trigger automatically download')
        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)
        if not re.search('\^SUSMC: "ConMgr/Fallback/',test.dut.at1.last_response):
            test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")
            test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)
            test.expect(re.search('\^SUSMC: "ConMgr/Fallback/',test.dut.at1.last_response))
        test.dut.dstl_activate_cm_settings()
        test.log.step(
            f'{step}.6:Bootstrap profile is shown per default Jersey Telecom. If instant connect sim is in use change it to EasyConnect elso do nothing')
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify(
                'at^susmc="ConMgr/Profile/Table",0,"89000000000000000040","EasyConnect Provisioning",2,1,"JTM2M","","",0,0')
        else:
            test.log.info("ELISA sim is in use therefor do not need to change connection manager table")
        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)
        test.log.step(f'{step}.7:List all profiles in connection manager table')
        test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table"')
    return True

def record_iccid(test,iccids,index):
    imei = test.dut.dstl_get_imei()
    iccid = test.dut.dstl_get_all_iccids(test.rest_client,imei)
    iccids[index]=iccid
    test.log.info(f'iccid is {iccid}')
    if iccid.__len__() != 1:
        test.log.error(f'Should be only one iccid link to {imei}.')
        return False
    return True

def record_iccid_switch(test,iccids,index):
    get_profile_list(test)
    result = re.search('\^SUSMA: "LPA/Profiles/Info",2,[01],"(\d+)","",.*', test.dut.at1.last_response)
    if result is None:
        test.log.error('new iccid is wrong')
        return False
    else:
        iccids[index]=result.group(1)
        test.log.info(f'new iccid is {iccids[index]}')
    return True

def print_time_consumption_report(test,info, iccids,time_consumption_dict):
    
    for key in time_consumption_dict:
        test.log.info('*' * 10 + f'{info}:Time consumption of {key}' + '*' * 10)
        list_1=[]
        time_list = time_consumption_dict[key]
        for i in range (0,time_list.__len__()):
            if time_list[i]==0:
                continue
            test.log.info(f'{i}:iccid={iccids[i]} , time_consumption={time_list[i]}')
            list_1.append(time_list[i])
        if list_1.__len__()==0:
            test.log.error(f'Time consumption list of {key} is null.' )
        else:
            test.log.info(f'The minimum value of {key} is {min(list_1)}')
            test.log.info(f'The maximum value of {key} is {max(list_1)}')
            test.log.info(f'The average value of {key} is {sum(list_1)/list_1.__len__()}')
    
    return

def fallback_to_bootstrap_enalbed(test, step):  # same with init_new
    test.log.step(f'{step}.1: Check all available profiles - Start')
    profile_list = get_profile_list(test)
    if len(profile_list) == 2:
        test.log.info("No operational profile should be deleted!!!")
        test.log.step(f'{step}.2: Activate bootstrap profile.')
        test.attempt(test.dut.dstl_activate_bootstrap_and_apns, retry=3, sleep=5)
        test.log.step(f'{step}.3: Stop mods agent,disable download mode.')
        test.dut.dstl_stop_mods_agent()
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*')
        test.log.step(f'{step}.4: Drop all broken subscriptions and create them again..')
        cleanup_broken_iccids(test)
        return True
    else:
        test.log.info("Operational profile found,it should be deleted!!!")
        test.log.step(f'{step}.2: Initialise all settings for MODS')
        test.expect(test.dut.dstl_init_all_mods_settings())
        test.log.step(f'{step}.3: Stop MODS agent')
        test.expect(test.dut.dstl_stop_mods_agent())
        
        test.log.step(f'{step}.4: Set download mode to 11')
        test.expect(test.dut.dstl_set_download_mode_wo_agent(download_mode=11))
        
        test.log.step(f'{step}.5: Activate LPA engine')
        activate_lpa_engine(test)
        
        test.log.step(f'{step}.6: Enable bootstrap and JTM2M apns - Start')
        test.attempt(test.dut.dstl_activate_bootstrap_and_apns, retry=3, sleep=5)
        test.sleep(30)
        test.log.step(f'{step}.7: Delete all subscription on module')
        #test.attempt(test.dut.dstl_delete_all_subscriptions_on_module,profile_list, retry=3, sleep=10)
        if not test.dut.dstl_delete_all_subscriptions_on_module(profile_list):
            WORKAROUND_SRV03_3305(test,profile_list)
        test.dut.at1.send_and_verify('at^susma?', ".*OK.*")

        test.log.step(f'{step}.8: Check network registration')
        test.expect(register_network(test))
            
        test.log.step(f'{step}.9: Active PDP context.')
        activate_internet_connection(test)
        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR', '\+CGPADDR: 1,"\d+.\d+.\d+.\d+"'))
        
        test.log.step(f'{step}.10: Send pending notifications')
        test.expect(send_pending_notifications(test))
        test.log.step(
            f'{step}.11: Get all subscriptions IDs which belong to your IMEI and delete all subscriptions - Start')
        imei = test.dut.dstl_get_imei()
        iccids = test.dut.dstl_get_all_iccids(test.rest_client,imei)
        subscription_ids = test.dut.dstl_get_all_subscription_ids(test.rest_client,imei)
        subscriptions = test.dut.dstl_get_all_subscriptions(test.rest_client, imei)
        test.log.info(
            "We have decided to use drop function instead of delete to delete all ICCIDs from MODS server")
        test.dut.dstl_drop_all_subscriptions(test.rest_client, subscription_ids, iccids)

        test.log.step(f'{step}.12: Create already deleted subscriptions back on MODS')
        result, test.iccid_results_list = test.dut.dstl_create_all_subscriptions(test.rest_client, subscriptions)
        test.expect(result)
        test.log.step(f'{step}.13: Drop all broken subscriptions and create them again..')
        cleanup_broken_iccids(test)
        return True

def WORKAROUND_SRV03_3305(test,profile_list):
    test.expect(False,msg='SRV03_3305 maybe happened.')
    test.log.com('++++ WORKAROUND_SRV03_3305 - Start *****')
    '''
    SRV03_3305 restart always happens between activate_lpa_engine and dstl_delete_all_subscriptions_on_module,
    cause dstl_delete_all_subscriptions_on_module failed.So if it failed,repeat this part.Otherwise it will cause create
    subscriptions error.
    '''
    test.sleep(15)
    activate_lpa_engine(test)
    test.attempt(test.dut.dstl_activate_bootstrap_and_apns, retry=3, sleep=5)
    test.sleep(30)
    test.log.info('Delete all subscription on module - Start')
    test.attempt(test.dut.dstl_delete_all_subscriptions_on_module,profile_list, retry=3, sleep=10)
    test.log.com('++++ WORKAROUND_SRV03_3305 - End *****')
    return True
def WORKAROUND_SRV03_3305_switch(test):
    test.expect(False, msg='SRV03_3305 maybe happened.')
    test.sleep(15)
    if test.dut.at1.send_and_verify('at^susma="LPA/Profiles/Delete",2', 'OK'):
        return True
    test.log.com('++++ WORKAROUND_SRV03_3305 - Start *****')
    test.dut.dstl_init_all_mods_settings()
    activate_lpa_engine(test)
    test.attempt(test.dut.at1.send_and_verify, 'at^susma="LPA/Profiles/Enable",1', 'OK', retry=3, sleep=5)
    #test.dut.at1.wait_for('^SSIM READY')
    test.sleep(30)
    test.log.info('Delete profile 2')
    test.attempt(test.dut.at1.send_and_verify, 'at^susma="LPA/Profiles/Delete",2', 'OK', retry=3, sleep=5)
    test.log.com('++++ WORKAROUND_SRV03_3305 - End *****')
    return True
    
def activate_lpa_engine(test):
    test.dut.at1.send_and_verify("at^susmc=\"LPA/Engine/URC\",1", ".*OK.*")
    test.expect(test.dut.at1.send_and_verify('at^susma="LPA/Engine",1', 'OK'))
    i=1
    while i<=5:
        if '^SUSMA: "LPA/Engine",2' in test.dut.at1.last_response:
            break
        elif '^SUSMA: "LPA/Engine",12' in test.dut.at1.last_response:
            test.expect(False,msg='SRV03-3078 happened.')
            test.log.com('++++ WORKAROUND SRV03-3078 - Start *****')
            test.log.info('Restart for SRV03-3078')
            test.dut.dstl_restart()
            if test.cmw500_network is True:
                test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60)
            else:
                test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"', timeout=10)
            activate_lpa_engine(test)
            test.log.com('++++ WORKAROUND SRV03-3078 - End *****')
            return
        else:
            test.dut.at1.wait_for('\^SUSMA: "LPA/Engine",\d+', timeout=10)
            test.expect(test.dut.at1.send_and_verify('at^susma="LPA/Engine",1', 'OK'))
            i+=1

    test.dut.at1.send_and_verify('at^susma?', '\^SUSMA: "LPA/Engine",2.*OK.*')
    return
    
def register_network(test):
    if test.cmw500_network is True:
        test.dut.at1.send_and_verify("at+cereg?", expect="OK")
        if re.search('CEREG: [0124],1', test.dut.at1.last_response):
            return True
        test.attempt(test.dut.at1.send_and_verify, 'AT+COPS=0,,,7', 'OK', retry=10, sleep=1)
        time.sleep(1)
        if test.dut.at1.send_and_verify('at+cereg?', 'CEREG: [0124],1.*OK'):
            return True
        else:
            return False
    if test.rat =='gsm':
        test.dut.at1.send_and_verify("at+creg?", expect="OK")
        if re.search('CREG: [012],5', test.dut.at1.last_response):
            return True
        test.attempt(test.dut.at1.send_and_verify, 'AT+COPS=,,,0', 'OK', retry=10, sleep=1)
        if test.dut.at1.send_and_verify('at+creg?', 'CREG: [012],5.*OK'):
            return True
        else:
            return False
    elif test.rat == 'cat_nb':
        test.dut.at1.send_and_verify("at+cereg?", expect="OK")
        if re.search('CEREG: [0124],5', test.dut.at1.last_response):
            return True
        test.attempt(test.dut.at1.send_and_verify, 'AT+COPS='+test.man_network_selection_nb, 'OK', retry=10, sleep=5)
        if test.dut.at1.send_and_verify('at+cereg?', 'CEREG: [0124],5.*OK'):
            return True
        else:
            return False
    elif test.rat == 'catm1':
        test.dut.at1.send_and_verify("at+cereg?", expect="OK")
        if re.search('CEREG: [0124],5', test.dut.at1.last_response):
            return True
        test.attempt(test.dut.at1.send_and_verify, 'AT+COPS=,,,7', 'OK', retry=10, sleep=1)
        if test.dut.at1.send_and_verify('at+cereg?', 'CEREG: [0124],5.*OK'):
            return True
        else:
            return False
    else:
        test.log.error('For serval,only support rat 0/7/8')
        test.expect(False,critical=True)
    return True
def check_network_registration(test):
    if test.dut.at1.send_and_verify("at+cereg?", expect=".*CEREG: [0124],[15].*OK"):
        return True
    else:
        if test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60):
            return True
        else:
            test.log.warning('Automatic registration is failed.')
            return False

def connectivity_switch_module_configure(test, step):
    test.require_parameter('profile_number_before_download', default=3)
    test.log.step(f'{step}.1:Set Rule ID')
    if test.cmw500_network is True:
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",RS Test Profile', expect='.*OK.*'))
    else:
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",UNICORN-POC', expect='.*OK.*'))
    test.log.step(f'{step}.2:Set Download Mode to 1')
    test.attempt(test.dut.at1.send_and_verify, 'AT^SRVCFG="MODS","usm/downloadMode",1', 'OK', retry=3, sleep=10)
    test.log.step("f'{step}.3:Enable URC's")
    test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/Ext/URC",1', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Profiles/Download/URC",1',
                                             expect='^SUSMC: "LPA/Profiles/Download/URC",1'))
    test.expect(test.dut.at1.send_and_verify('at+creg=2', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Engine/URC",1', expect='^SUSMC: "LPA/Engine/URC",1'))

    test.log.step(f'{step}.4:Create job connectivity switch')
    test.jobid=create_job_for_connectivity_switch(test)

    if test.unicorn_step_version == 'unicorn_step_2':
        test.log.step(
            f'{step}.8:Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr will trigger automatically download')
        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)
        if not re.search('\^SUSMC: "ConMgr/Fallback/', test.dut.at1.last_response):
            test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")
            test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)
            test.expect(re.search('\^SUSMC: "ConMgr/Fallback/', test.dut.at1.last_response))
        test.dut.dstl_activate_cm_settings()
        test.log.step(
            f'{step}.9:Bootstrap profile is shown per default Jersey Telecom. If instant connect sim is in use change it to EasyConnect elso do nothing')
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify(
                'at^susmc="ConMgr/Profile/Table",0,"89000000000000000040","EasyConnect Provisioning",2,1,"JTM2M","","",0,0')
        else:
            test.log.info("ELISA sim is in use therefor do not need to change connection manager table")
        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)
        test.log.step(f'{step}.10:List all profiles in connection manager table')
        test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table"')

    return True

def create_job_for_connectivity_switch(test):
    # Properties for connectivity switch job.
    imei = test.dut.dstl_get_imei()
    test.require_parameter('stage_index', default='0')
    test.require_parameter('time_to_sleep', default='0')
    name = f"Auto_switch:{imei}_{test.stage_index}_{test.time_to_sleep}"
    description = "Connectivity switch performance test"
    IS_Siminn_internet_1_id="69c42d32-a206-4158-b014-bdb56fa27761"
    RS_test_id='b20bc6ea-c9e9-42a7-85bb-065af740341d'
    if test.cmw500_network is True:
        poolid=RS_test_id
    else:
        poolid=IS_Siminn_internet_1_id
    test.log.step('Create connectivity switch')
    job = create_connectivity_switch(name, description, poolid)
    # TODO Handle Errors
    log_body(job.json())
    test.expect(job.status_code == 200)

    test.log.step('Get device with imei')
    target = get_device_with_imei(imei)
    # TODO Handle Errors
    log_body(target.json())
    test.expect(target.status_code == 200)

    test.log.step('Create job target')
    job_id = job.json()['id']
    target_id = target.json()['id']
    job = create_job_target(job_id, target_id)
    # TODO Handle Errors
    log_body(job.json())
    test.expect(job.status_code == 200)

    test.log.step('Schedule job')
    # Job schedule properties.
    current_time = datetime.datetime.now() - datetime.timedelta(hours=8)
    schedule_from = f'{(current_time).isoformat()}Z'
    schedule_to = f'{(current_time + datetime.timedelta(seconds=1800)).isoformat()}Z'
    job = schedule_job(job_id, schedule_from, schedule_to)

    # TODO Handle Errors
    log_body(job.json())
    test.expect(job.status_code == 200)
    return job_id
def record_time_consumption(test,time_consumption_dict,index):
    test.dut.dstl_start_mods_agent()
    if not test.dut.at1.send_and_verify('at^srvctl="MODS","status"','\^SRVCTL: "MODS","status",1,"service is running"'):
        test.expect(False,msg='SRV03-3543 happened:Start mods agent failed,restart module and try again.')
        test.log.com('++++ WORKAROUND FOR SRV03-3543 - Start *****')
        test.dut.dstl_restart()
        if test.cmw500_network is True:
            test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60)
        else:
            test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"', timeout=10)
        test.expect(register_network(test))
        activate_lpa_engine(test)
        test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/Ext/URC",1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Profiles/Download/URC",1',
                                                 expect='^SUSMC: "LPA/Profiles/Download/URC",1'))
        test.expect(test.dut.at1.send_and_verify('at+creg=2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Engine/URC",1', expect='^SUSMC: "LPA/Engine/URC",1'))
        test.expect(test.dut.dstl_start_mods_agent(),critical=True,msg='Start mods agent failed.')
        test.log.com('++++ WORKAROUND FOR SRV03-3543- End *****')
    start=time.time()
    while not test.dut.at1.wait_for('\^SRVACT: "MODS","srv","registered"', timeout=30):
        test.dut.at1.send_and_verify('at^smoni', 'OK')
        test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', 'OK')
        if ",registered" in test.dut.at1.last_response:
            test.log.error('Device is registered,but no ^SRVACT urc appear.')
            break
        else:
            if time.time() - start > 300:
                test.expect(False, msg='Timeout!Device register failed.')
                check_status(test)
                if test.jobid:
                    if test.dialup_start:
                        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, "Dial-up Connection")
                    abort_job(test.jobid)
                return False
    end = time.time()
    time_consumption_dict['register device'][index]=(end - start)
    test.log.info(f'Time consumption of register device is {end - start}')
    if test.dut.at1.wait_for('\^SUSMA: "LPA/Profiles/Download",0x\S+', timeout=600):
        if '^SUSMA: "LPA/Profiles/Download",0x0000' in test.dut.at1.last_response:
            start = end
            end = time.time()
            time_consumption_dict['download profile'][index] = (end - start)
            test.log.info(f'Time consumption of download profile is {end - start}')
        elif '^SUSMA: "LPA/Ext/Urc","1","Failed to Send PIR notification to server"' in test.dut.at1.last_response:
                test.log.info('Failed to Send PIR notification to server,should continue to restart.')
                start = end
                end = time.time()
        elif '^SUSMA: "LPA/Profiles/Download",0x231D' in test.dut.at1.last_response:
            test.log.warning('The first download failed with 0x231D,wait for retry.But will not record time consumption of this time.')
            if test.dut.at1.wait_for('\^SUSMA: "LPA/Profiles/Download",0x\S+', timeout=600):
                if '^SUSMA: "LPA/Profiles/Download",0x0000' in test.dut.at1.last_response:
                    test.log.info('The second download is successful.')
                    start = end
                    end = time.time()
                else:
                    test.log.warning('The second download failed again.')
                    register_network(test)
                    check_status(test)
                    return False
            else:
                test.log.error('Timeout!Second download failed.And no download result urc appear.')
                check_status(test)
                return download_timeout(test)
        else:
            test.log.warning('The first download failed with other error code(not 0x231D).')
            register_network(test)
            check_status(test)
            return False
    else:
        test.log.error('Timeout!Download failed.And no download result urc appear.')
        check_status(test)
        return download_timeout(test)
    test.dut.at1.read(append=True)
    if test.dut.at1.wait_for("\^SYSSTART", timeout=300):
        test.dut.at1.read(append=False)
        start = end
        end = time.time()
        test.dut.at1.wait_for('\^SSIM READY')
    else:
        test.dut.at1.read(append=False)
        test.log.error('Timeout!Trigger restart failed.')
        check_status(test)
        return False
    time_consumption_dict['trigger restart'][index] = (end - start)
    test.log.info(f'Time consumption of trigger restart is {end - start}')
    if check_network_registration(test):
        start = end
        end = time.time()
    else:
        if register_network(test):
            start = end
            end = time.time()
        else:
            test.log.error('Register network failed')
            check_status(test)
            return False
    time_consumption_dict['register network'][index] = (end - start)
    test.log.info(f'Time consumption of register network is {end - start}')
    check_after_restart(test)

    return True

def download_timeout(test):
    result = True
    if test.dialup_start==True:
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, "Dial-up Connection")
    if test.jobid:
        job_target_byte = get_job_targets(test.jobid)
        job_target_dict = eval(str(job_target_byte._content, 'utf-8')[1:-1])
        status = job_target_dict["status"]
        test.log.warning(f'Current job(id={test.jobid}) is failed, status is "{status}"')
        test.log.com(job_target_dict)
        if status == 'suspended':
            result=True
        else:
            result=False
        abort_job(test.jobid)
    return result

def check_after_restart(test):
    test.log.info('Register_network and do more test after finish activation.')
    if not register_network(test):
        test.expect(False, msg='Register network failed')
        check_status(test)
        return False
    test.log.info("Call ping if internet connection is established via operational profile")
    test.attempt(test.dut.at1.send_and_verify, 'AT^SICA=1,1', 'OK', retry=3, sleep=10)
    test.sleep(5)
    test.dut.at1.send_and_verify('at^smoni', '.*OK.*')
    test.dut.at1.send_and_verify('at^sica?', '.*OK.*')
    test.dut.at1.send_and_verify('at+cgpaddr', '.*OK.*')
    if test.cmw500_network is True:
        ping_address = '"www.baidu.com"'
    else:
        ping_address = '"www.google.com"'
    if not test.dut.at1.send_and_verify(f'AT^SISX=Ping,1,{ping_address},5', '.*OK.*'):
        test.dut.at1.send_and_verify('at+cops?', '.*OK.*')
        test.dut.at1.send_and_verify('at^sica?', '.*OK.*')
        if '^SICA: 1,0' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('at^sica=1,1', '.*OK.*')
        test.dut.at1.send_and_verify('at+cgpaddr', '.*OK.*')

    test.expect(test.dut.at1.send_and_verify(f'AT^SISX=Ping,1,{ping_address},5', '.*OK.*'))

    if test.unicorn_step_version == 'unicorn_step_2':
        test.log.info("Show cm table")
        test.dut.dstl_show_cm_table()
    test.log.info("Check download mode and apn after switch")
    test.expect(
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode"', '^SRVCFG: "MODS","usm/downloadMode","2"'))
    if test.cmw500_network is True:
        test.expect(test.dut.dstl_check_apn_and_mods_apns(apn="3gpp.test"))
    else:
        test.expect(test.dut.dstl_check_apn_and_mods_apns(apn="internet"))

    test.expect(len(get_profile_list(test)) == (test.profile_number_before_download + 1),
                msg='Profile number is wrong,after continue to finish profile switch.')
    result = re.search(f'\^SUSMA: "LPA/Profiles/Info",{test.profile_number_before_download},1,"\d+",',
                       test.dut.at1.last_response)
    if not result:
        test.expect(False, msg='New profile activation failed.')
    return True

def check_status(test):
    test.log.info('Check status,when error happens.')
    test.dut.at1.send_and_verify_retry("at^smoni", expect="OK")
    test.dut.at1.send_and_verify('at^susma?', 'OK')
    test.dut.at1.send_and_verify('at^susmc?', 'OK')
    test.dut.at1.send_and_verify('at+cgdcont?', 'OK')
    test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', 'OK')
    return

def abnormal_condition_during_connectivity_activation(test,step,condition):
    test.log.info(f'stage index is {test.stage_index}, time to sleep is {test.time_to_sleep}')
    test.dut.devboard.send_and_verify("at")
    test.log.step(f'{step}.1 Start mods agent.')
    test.expect(test.dut.dstl_start_mods_agent())

    if test.stage_index == 0:
        test.log.step(f'{step}.2 {condition} during register device.')
        test.sleep(test.time_to_sleep)
        test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', 'OK')
        if ",registered" not in test.dut.at1.last_response:
            eval(condition)(test)
            test.time_to_sleep += 2
            return True
        else:
            test.log.info(f'{condition} during register device test finish.')
            test.stage_index += 1
            test.time_to_sleep = 1
    else:
        test.log.step(f'{step}.2 No need {condition} during register device.')
        start = time.time()
        while not test.dut.at1.wait_for('\^SRVACT: "MODS","srv","registered"', timeout=30):
            test.dut.at1.send_and_verify('at^smoni', 'OK')
            test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', 'OK')
            if ",registered" in test.dut.at1.last_response:
                test.log.error('Device is registered,but no ^SRVACT urc appear.')
                break
            else:
                if time.time() - start > 300:
                    test.expect(False, msg='Timeout!Device register failed.')
                    check_status(test)
                    if test.jobid:
                        abort_job(test.jobid)
                    return False
    if test.stage_index == 1:
        test.log.step(f'{step}.3 {condition} during download profile.')
        test.sleep(test.time_to_sleep)
        test.dut.at1.read(append=True)
        if not re.search('\^SUSMA: "LPA/Profiles/Download",0x\S+', test.dut.at1.last_response):
            test.dut.at1.append(False)
            eval(condition)(test)
            test.time_to_sleep += 10
            return True
        else:
            if '^SUSMA: "LPA/Profiles/Download",0x0000' in test.dut.at1.last_response:
                test.log.info(f'{condition} during download profile test finish.')
                test.stage_index += 1
                test.time_to_sleep = 1
            else:
                test.log.error('First download failed,will not power off/loss network in this loop')
                test.dut.at1.append(False)
                test.dut.at1.wait_for("\^SYSSTART\r\n", timeout=600)
                register_network(test)
                return False
    else:
        test.log.step(f'{step}.3 No need {condition} during download profile.')
        if test.dut.at1.wait_for('\^SUSMA: "LPA/Profiles/Download",0x\S+', timeout=600):
            if '^SUSMA: "LPA/Profiles/Download",0x231D' in test.dut.at1.last_response:
                if '^SUSMA: "LPA/Ext/Urc","1","Failed to Send PIR notification to server"' not in test.dut.at1.last_response:
                    test.log.warning('First download failed')
                    if test.dut.at1.wait_for('\^SUSMA: "LPA/Profiles/Download",0x\S+', timeout=600):
                        if '^SUSMA: "LPA/Profiles/Download",0x0000' not in test.dut.at1.last_response:
                            test.log.error('Second download failed.')
                            test.dut.at1.append(False)
                            check_status(test)
                            return False
                    else:
                        test.expect(False, msg='Timeout!Second download failed.And no download result urc appear.')
                        test.dut.at1.append(False)
                        check_status(test)
                        return False
            elif '^SUSMA: "LPA/Profiles/Download",0x0000' not in test.dut.at1.last_response:
                    test.log.error('Download failed.')
                    test.dut.at1.append(False)
                    check_status(test)
                    return False
        else:
            test.expect(False, msg='Timeout!Download failed.And no download result urc appear.')
            test.dut.at1.append(False)
            check_status(test)
            return False
    if test.stage_index == 2:
        test.log.step(f'{step}.4 {condition} during trigger restart.')
        test.sleep(test.time_to_sleep)
        test.dut.at1.read(append=True)
        if not re.search('\^SYSSTART\r\n', test.dut.at1.last_response):
            test.dut.at1.append(False)
            eval(condition)(test)
            test.time_to_sleep += 10
            return True
        else:
            test.log.info(f'{condition} during trigger restart test finish.')
            test.dut.at1.append(False)
            test.stage_index = 3
            test.time_to_sleep = 1
            check_after_restart(test)
    else:
        test.fail('Please check test flow')
    return True


def power_off(test):
    test.log.step('Power off !!!')
    test.condition="power_off"
    test.dut.dstl_turn_off_vbatt_via_dev_board()
    test.sleep(60)
    test.dut.dstl_turn_on_vbatt_via_dev_board()
    test.dut.dstl_turn_on_igt_via_dev_board()
    test.dut.at1.wait_for("SYSSTART", timeout=300)
    test.expect(register_network(test))
    continue_after_abnormal_condition(test)
    return

def network_loss(test):
    test.condition = "network_loss"
    test.log.step('Network loss !!!')
    test.dut.at1.append(True)
    test.dut.at1.send_and_verify('at+cereg=2', 'OK')
    test.dut.at1.send_and_verify("at+cereg?", expect="CEREG: 2,5.*OK")
    test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=3, mode='OFF')
    test.attempt(test.dut.at1.send_and_verify, 'at+cereg?', '\+CEREG: \d,[024]', retry=10, sleep=30)
    test.dut.at1.send_and_verify('at^smoni', 'OK')
    test.sleep(30)
    test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=3, mode='ON1')
    continue_after_abnormal_condition(test)
    return
    
def continue_after_abnormal_condition(test):
    if test.condition=="power_off":
        test.log.step('Continue after power off!!!')
        test.dut.at1.send_and_verify("at+creg=2", ".*OK.*")
        test.dut.at1.send_and_verify("at^susmc=\"LPA/Ext/URC\",1", ".*OK.*")
        test.dut.at1.send_and_verify("at^susmc=\"LPA/Engine/URC\",1", ".*OK.*")
        test.dut.at1.send_and_verify("at^susmc=\"LPA/Profiles/Download/URC\",1", ".*OK.*")
    elif test.condition=="network_loss":
        test.log.step('Continue after network loss!!!')
        test.dut.at1.append(False)
        if '^SYSSTART' in test.dut.at1.last_response:
            test.log.info('Module has triggered restart.')
            check_after_restart(test)
            return True
    else:
        test.expect(False,msg='Test condition is wrong.')
    profile_number = len(get_profile_list(test))
    if profile_number == test.profile_number_before_download:
        test.log.info(f'Profile number is {test.profile_number_before_download} after power off or network loss.')
        continue_to_download_or_switch_profile(test)
    elif profile_number == (test.profile_number_before_download + 1):
        test.log.info(f'Profile number is {test.profile_number_before_download+1} after power off or network loss.')
        if re.search(f'\^SUSMA: "LPA/Profiles/Info",{test.profile_number_before_download},1,"\d+",',test.dut.at1.last_response):
            test.log.info('Download and profile switch is complete.')
        if re.search(f'\^SUSMA: "LPA/Profiles/Info",{test.profile_number_before_download},0,"\d+",',test.dut.at1.last_response):
            test.log.info('Download is complete,but profile switch is not.')
            continue_to_download_or_switch_profile(test)
    else:
        test.log.warning('Profile number seems is not correct,please check your flow.')
    check_after_restart(test)
    return True

def continue_to_download_or_switch_profile(test):
    if test.condition=="power_off":
        test.expect(test.dut.dstl_start_mods_agent())
        start = time.time()
        while not test.dut.at1.wait_for('\^SRVACT: "MODS","srv","registered"', timeout=30):
            test.dut.at1.send_and_verify('at^smoni', 'OK')
            test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', 'OK')
            if ",registered" in test.dut.at1.last_response:
                test.log.error('Device is registered,but no ^SRVACT urc appear.')
                break
            else:
                if time.time() - start > 600:
                    test.expect(False, msg='Timeout!Device register failed.')
                    check_status(test)
                    if test.jobid:
                        abort_job(test.jobid)
                    return False
    elif test.condition=="network_loss":
        test.expect(register_network(test))
        test.expect(test.dut.dstl_start_mods_agent())
        test.log.com('++++ WORKAROUND for job suspend issue - Start *****')
        test.dut.at1.send_and_verify('AT^SRVACT="MODS","update"')
        if '\^SRVACT: "MODS","update","finished"' not in test.dut.at1.last_response:
            test.dut.at1.wait_for('\^SRVACT: "MODS","update","finished"', timeout=60)
        test.log.com('++++ WORKAROUND for job suspend issue - End *****')
    else:
        test.expect(False,msg='Test condition is wrong.')

    if test.profile_number_before_download == 3:
        test.sleep(10)
        job_target_byte = get_job_targets(test.jobid)
        job_target_dict = eval(str(job_target_byte._content, 'utf-8')[1:-1])
        status = job_target_dict["status"]
        if "reason" in job_target_dict.keys():
            reason = job_target_dict["reason"]
        if status == 'failed':
            if reason == 'Unexpected SM procedure result: 0 (procedure not started yet or ongoing)':
                test.log.info(f'Current job(id={test.jobid}) is failed, , reason is "{reason}".Create new job to continue.')
                create_job_for_connectivity_switch(test)
            else:
                test.log.warning(f'Current job(id={test.jobid}) is failed, reason is "{reason}"')
                test.log.com(job_target_dict)
        else:
            test.log.info(f'Current job(id={test.jobid}) state is "{status}"')
    if not test.dut.at1.wait_for("\^SYSSTART\r\n", timeout=300):
        test.expect(False, msg='Timeout!Trigger restart failed.')
        check_status(test)
        return False
    else:
        test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"')
        return True
def get_profile_list(test):
    test.log.info('Get profile list.')
    list = []
    profile_info = {}
    test.dut.at1.send_and_verify("AT^SUSMA?", 'OK')
    i = 1
    while '+CME ERROR: unknown' in test.dut.at1.last_response or '^SUSMA: "LPA/Profiles/Info",,,"","","","",' in test.dut.at1.last_response:
        test.sleep(2)
        test.dut.at1.send_and_verify("AT^SUSMA?", 'OK')
        i += 1
        if i>3:
            break
    if 'OK' in test.dut.at1.last_response:
        response = test.dut.at1.last_response
        lines = response.split('\n')
        for i in range(0, len(lines)):
            if ("LPA/Profiles/Info") in lines[i]:
                test.log.com("Profile info (" + str(i) + "): " + str(lines[i]))
                # print(lines[i])
                info = lines[i].split(',')
                profile_info["profile_id"] = info[1]
                profile_info["profile_state"] = info[2]
                profile_info["iccid"] = info[3]
                profile_info["provider_name"] = info[5]
                profile_info["profile_name"] = info[6]
                profile_info["profile_class"] = info[7].replace("\r", "")
                list.append(dict(profile_info))
        return list
    else:
        test.log.error('Profile number is wrong.')
        return []

def fallback_to_original_operational_profile(test, step):  # same with init_new
    test.log.step(f'{step}.1: Check all available profiles - Start')
    i=0
    profile_number=len(get_profile_list(test))

    while profile_number<=1 and i<3:
        test.sleep(60)
        profile_number = len(get_profile_list(test))
        i+=1
    if profile_number == 4:
        iccids = []
        subscription_ids = []
        new_iccid = re.search(f'\^SUSMA: "LPA/Profiles/Info",3,[01],"(\d+)","",.*', test.dut.at1.last_response).group(1)
        new_subscription_id = get_subscription_id_by_iccid(new_iccid)
        test.log.info('new iccid is ' + new_iccid + ' ,new new subscription id is ' + new_subscription_id)
        iccids.append(new_iccid)
        subscription_ids.append(new_subscription_id)
        test.log.step(f'{step}.2: Initialise all settings for MODS')
        test.expect(test.dut.dstl_init_all_mods_settings())
        test.log.step(f'{step}.3: Stop MODS agent')
        test.expect(test.dut.dstl_stop_mods_agent())
        
        test.log.step(f'{step}.4: Set download mode to 11')
        test.expect(test.dut.dstl_set_download_mode_wo_agent(download_mode=11))

        test.log.step(f'{step}.5: Activate LPA engine')
        activate_lpa_engine(test)
        
        test.log.step(f'{step}.6: Activate  profile 1')
        test.attempt(test.dut.at1.send_and_verify,'at^susma="LPA/Profiles/Enable",2','OK',retry=3, sleep=5)
        test.dut.at1.wait_for('^SSIM READY')

        test.log.step(f'{step}.7: Check network registration and apn')
        if not check_network_registration(test):
            test.expect(register_network(test))
        test.expect(test.dut.at1.send_and_verify('at+cgdcont?','\+CGDCONT: 1,"IP","internet".*OK'))

        test.log.step(f'{step}.8: Delete profile 3')
        counter=1
        while counter<=3 and not test.dut.at1.send_and_verify('at^susma="LPA/Profiles/Delete",3', 'OK'):
            time.sleep(5)
            counter+=1
        if counter==3 and '+CME ERROR: operation temporary not allowed' in test.dut.at1.last_response:
            test.expect(False,msg='Fail to delete profile 3.')
        test.dut.at1.send_and_verify('at^susma?', ".*OK.*")

        test.log.step(f'{step}.9: Active PDP context.')
        activate_internet_connection(test)
        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR', '\+CGPADDR: 1,"\d+.\d+.\d+.\d+"'))
        
        test.log.step(f'{step}.10: Send pending notifications')
        test.expect(send_pending_notifications(test))
        imei = test.dut.dstl_get_imei()
        subscriptions = test.dut.dstl_get_all_subscriptions(test.rest_client, imei)
        for sub in subscriptions:
            if new_iccid in sub['iccid']:
                new_sub=sub
                break
        test.log.info(
            "We have decided to use drop function instead of delete to delete all ICCIDs from MODS server")
        test.log.step(
            f'{step}.11: drop subscription_id: {new_subscription_id}, iccid: {new_iccid}')
        test.expect(test.dut.dstl_drop_all_subscriptions(test.rest_client,subscription_ids, iccids))
        test.log.step(f'{step}.12: Create already deleted subscriptions back on MODS')
        result, test.iccid_results_list = test.dut.dstl_create_single_subscription(test.rest_client, new_sub['iccid'], new_sub['poolId'])
        test.expect(result)
        test.log.step(f'{step}.13: Drop all broken subscriptions and create them again..')
        cleanup_broken_iccids(test)
        result=True
    elif profile_number == 3:
        test.log.info('profile number is 3')
        test.log.step(f'{step}.2: Stop mods agent,disable download mode.')
        test.dut.dstl_stop_mods_agent()
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*')
        test.log.step(f'{step}.3: Drop all broken subscriptions and create them again..')
        cleanup_broken_iccids(test)
        result = False
    else:
        test.log.error('profile number is wrong')
        test.expect(False,critical=True)

    return result
    

def send_pending_notifications(test):
    test.dut.at1.send_and_verify('AT^SUSMA="LPA/Ext/NotificationSent"','OK',timeout=120)
    if re.search('0x0000',test.dut.at1.last_response):
        return True
    elif '+CME ERROR: operation temporary not allowed' in test.dut.at1.last_response:
        test.sleep(60)
    elif re.search('0x231D', test.dut.at1.last_response):
        test.dut.at1.send_and_verify('AT^SUSMA="LPA/Ext/NotificationSent"', 'OK', timeout=120)
        if re.search('0x0000', test.dut.at1.last_response):
            return True
        elif '+CME ERROR: operation temporary not allowed' in test.dut.at1.last_response:
            test.sleep(60)
        elif re.search('0x231D', test.dut.at1.last_response):
            test.log.warning('SRV03-3538 happened.')
            test.log.com('++++ WORKAROUND SRV03-3538 - Start *****')
            test.dut.dstl_restart()
            if test.cmw500_network is True:
                test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60)
            else:
                test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"', timeout=10)
            test.expect(register_network(test))
            activate_lpa_engine(test)
            activate_internet_connection(test)
            test.log.com('++++ WORKAROUND SRV03-3538 - End *****')
        else:
            test.expect(register_network(test))
            activate_internet_connection(test)
        return send_pending_notifications(test)
    else:
        test.expect(register_network(test))
        activate_internet_connection(test)
    return send_pending_notifications(test)

def activate_internet_connection(test):
    test.attempt(test.dut.at1.send_and_verify, 'at^sica=1,1', 'OK', retry=2, sleep=10)
    if '+CME ERROR: unspecified GPRS error' in test.dut.at1.last_response:
        test.expect(False, msg='SRV03-3484 happened.')
        test.log.com('++++ WORKAROUND FOR SRV03-3484 - Start *****')
        test.expect(test.dut.at1.send_and_verify('AT^SMONI', 'OK'))
        test.dut.dstl_restart()
        if test.cmw500_network is True:
            test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60)
        else:
            test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"', timeout=10)
        test.expect(register_network(test))
        activate_lpa_engine(test)
        test.attempt(test.dut.at1.send_and_verify, 'at^sica=1,1', 'OK', retry=2, sleep=10)
        test.log.com('++++ WORKAROUND FOR SRV03-3484 - END *****')
    return True
    
def get_subscription_id_by_iccid(iccid):
    subscriptions = get_subscriptions().json()
    for i in subscriptions:
        if i['iccid'] == iccid:
            subsription_id=i['id']
    return subsription_id
   

def set_modes_register_update_time(test):
    test.dut.at1.send_and_verify('AT^snlwm2m="cfg/object",MODS,/1/0','OK')
    if '^SNLWM2M: "cfg/object","MODS","/1/0/1","86400"' in test.dut.at1.last_response:
        return True
    test.dut.at1.send_and_verify('AT^SNLWM2M="cfg","MODS","/1/0/1","86400"', 'OK')
    test.dut.at1.send_and_verify('AT^SNLWM2M="cfg/object",MODS,"/1/0",new', 'OK')
    test.dut.at1.send_and_verify('AT^snlwm2m="cfg/object",MODS,/1/0', 'OK')
    return True

#SRV03-4427
def disable_edrx(test):
    test.dut.at1.send_and_verify('AT+CEDRXS=0,4', 'OK')
    test.dut.at1.send_and_verify('AT+CEDRXS=0,5', 'OK')
    return

def cleanup_broken_iccids(test):
    test.log.info("Get all broken subscriptions belong to your imei")
    test.log.info("Broken subscriptions here means subscription_status=available and job_status=failed.")
    imei = test.dut.dstl_get_imei()
    subscriptions=get_subscriptions().json()
    subscriptions_to_drop = []
    iccids_to_drop = []
    subscription_ids_to_drop=[]
    for i in subscriptions:
        if i['status']=='available'and 'imei' in i.keys() and 'jobId' in i.keys():
            if i['imei']==imei:
                targets = get_job_targets(i['jobId']).json()
                if targets[0]['imei'] == imei and targets[0]['status'] == 'failed':
                    test.log.info('Find a broken subscription,information as below,we will drop and re-create it later.')
                    test.log.info(i)
                    subscriptions_to_drop.append(i)
                    iccids_to_drop.append(i['iccid'])
                    subscription_ids_to_drop.append(i['id'])
    if subscription_ids_to_drop ==[]:
        test.log.info('No broken subscriptions')
        return True
    test.log.info('Drop all broken subscriptions')
    test.dut.dstl_drop_all_subscriptions(test.rest_client,subscription_ids_to_drop, iccids_to_drop)
    test.log.info('Create already deleted subscriptions back on MODS')
    #subscriptions = test.dut.dstl_get_all_subscriptions(test.rest_client, imei)
    test.dut.dstl_create_all_subscriptions(test.rest_client, subscriptions_to_drop)
    return True

#SRV03-3217
def config_mask_of_CIoT_capability(test):
    test.expect(test.dut.at1.send_and_verify('at^scfg="radio/ciotopt"','OK'))
    if test.rat == 'cat_nb':
        if '^SCFG: "Radio/CIotOpt","8"' not in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('at^scfg="radio/ciotopt",8', 'OK'))
            test.dut.dstl_restart()
            if test.cmw500_network is True:
                test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60)
            else:
                test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"', timeout=10)
    else:
        if '^SCFG: "Radio/CIotOpt","15"' not in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('at^scfg="radio/ciotopt",15', 'OK'))
    return True

# def check_and_create_device(test):
#     test.rest_client = IotSuiteRESTClient()
#
#     # TEMPORARY solution. Should not be hardcoded. Group id of MigrationGroup
#     test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'
#     imei = test.dut.dstl_get_imei()
#     test.log.info("This is your IMEI: " + imei)
#     result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
#     return result