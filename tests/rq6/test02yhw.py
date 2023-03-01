import pandas as pd

filepath = r'C:\Users\T0259343\Desktop\test'
readfile = r'\ebs_run_all_test.log'
writefile = r'\result.log'
writecsv = r'\result.csv'
keywords = ['FAIL:']
withoutwords = ['Start Error', 'force_abnormal_flow']
result = []
resultfilter = []
tname_tnum = {
    'resmed_ehealth_downloadtasklist_normalflow.py': 'TC0107810.001',
    'resmed_ehealth_sendhealthdata_normal_flow.py': 'TC0107805.001',
    'resmed_ehealth_updatemodule_robustness_test_ef_b1.py': 'TC0107853.001',
    'resmed_ehealth_updatemodule_robustness_test_ef_b2.py': 'TC0107855.001',
    'resmed_ehealth_downloadfile_exceptional_flow_b.py': 'TC0107800.001',
    'resmed_ehealth_initmodule_normal_flow.py': 'TC0107803.001',
    'resmed_ehealth_updatemodule_robustness_test_ef_a.py': 'TC0107809.001',
    'resmed_ehealth_downloadfile_exceptional_flow_a.py': 'TC0107798.001',
    'resmed_ehealth_downloadfile_exceptional_flow_c.py': 'TC0107802.001',
    'resmed_ehealth_shutdownmodule_nf.py': 'TC0107795.001',
    'resmed_ehealth_basic_with_different_sim.py': 'TC0107811.001',
    'resmed_ehealth_updateapplication_normalflow.py': 'TC0107808.001',
    'resmed_ehealth_download_file_normal_flow.py': 'TC0107796.001',
    'resmed_ehealth_updatemodule_nf.py': 'TC0107807.001',
    'resmed_ehealth_disableflightmode_normalflow.py': 'TC0107792.001',
    'resmed_ehealth_sendhealthdata_af_a.py': 'TC0107851.001',
    'resmed_ehealth_shutdownmodule_stresstest.py': 'TC0107864.001',
    'resmed_ehealth_sendhealthdata_alternative_flow_a_exceptional_flow_a_b.py': 'TC0107852.001',
    'resmed_ehealth_sendhealthdata_stress.py': 'TC0107806.001',
    'resmed_ehealth_initmodule_alternative_flow_b_c.py': 'TC0107850.001',
    'resmed_ehealth_shut_down_module_normal_flow_stress_test.py': 'TC0107812.001',
    'resmed_ehealth_initmodule_alternative_flow_a.py': 'TC0107804.001',

    'ebs_alarmdevice_checknetwork_errorhanding_b.py': 'TC0108051.001',
    'ebs_alarmdevice_checknetwork_errorhanding_c.py': 'TC0108053.001',
    'ebs_alarmdevice_checknetwork_errorhanding_d.py': 'TC0108054.001',
    'ebs_alarmdevice_checknetwork_nf.py': 'TC0108042.001',
    'ebs_alarmdevice_receiveconfigration_errorhanding_b_c_d.py': 'TC0108059.001',
    'ebs_alarmdevice_receiveconfigration_nf.py': 'TC0108055.001',
    'ebs_alarmdevice_sendalarm_ef_b.py': 'TC0108044.001',
    'ebs_alarmdevice_sendalarm_ef_c.py': 'TC0108045.001',
    'ebs_alarmdevice_sendalarm_nf.py': 'TC0108043.001',
    'ebs_alarmdevice_sendheartbeat_ef_b.py': 'TC0108047.001',
    'ebs_alarmdevice_sendheartbeat_ef_c_d.py': 'TC0108048.001',
    'ebs_alarmdevice_sendheartbeat_nf.py': 'TC0108046.001',
    'ebs_alarmdevice_sendreport_ef_b.py': 'TC0108050.001',
    'ebs_alarmdevice_sendreport_ef_c_d.py': 'TC0108052.001',
    'ebs_alarmdevice_sendreport_nf.py': 'TC0108049.001',
    'ebs_alarmdevice_updateapplication_b_c_d.py': 'TC0108060.001',
    'ebs_alarmdevice_updateapplication_nf.py': 'TC0108058.001',

    'trakmate_trackingunit_updatemodule_ef02.py': 'TC0107884.001',
    'trakmate_trackingunit_updatemodule_ef01.py': 'TC0107883.001',
    'trakmate_trackingunit_updatemoduleIotsuite_nf03.py': 'TC0107882.001',
    'trakmate_update_module_nf_1.py': 'TC0107880.001',
    'trakmate_update_module_nf_2.py': 'TC0107881.001',
    'trakmate_update_application_exceptional_flow.py': 'TC0107863.001',
    'trakmate_update_application_normal_flow.py': 'TC0107862.001',
    'trakmate_switch_sim_profile_normal_flow.py': 'TC0107845.001',
    'trakmate_send_trackingdata_loadtest_nf.py': 'TC0107879.001',
    'trakmate_send_trackingdata_mqtt_ef.py': 'TC0107878.001',
    'trakmate_send_trackingdata_http_ef.py': 'TC0107877.001',
    'trakmate_send_trackingdata_tcp_ef.py': 'TC0107876.001',
    'trakmate_send_trackingdata_normal_flow.py': 'TC0107875.001',
    'trakmate_send_notification_normal_flow.py': 'TC0107865.001',
    'trakmate_send_alert_error_flow.py': 'TC0107874.001',
    'trakmate_send_alert_normal_flow.py': 'TC0107873.001',
    'trakmate_init_module_error_flow.py': '	TC0107872.001',
    'trakmate_init_module_normal_flow.py': 'TC0107871.001',
    'trakmate_execute_command_nf.py': 'TC0107826.001',
    'trakmate_execute_command_ef.py': 'TC0107844.001',
    'trakmate_execute_command_nf_duration.py': 'TC0107842.001',
    'trakmate_download_config_normal_flow.py': 'TC0107854.001',
    'trakmate_download_config_error_flow.py': 'TC0107861.001'
}
tname_responsible = {
    'resmed_ehealth_downloadtasklist_normalflow.py': 'Han, Feng',
    'resmed_ehealth_sendhealthdata_normal_flow.py': 'ding haofeng',
    'resmed_ehealth_updatemodule_robustness_test_ef_b1.py': 'ding haofeng',
    'resmed_ehealth_updatemodule_robustness_test_ef_b2.py': 'ding haofeng',
    'resmed_ehealth_downloadfile_exceptional_flow_b.py': 'Han, Feng',
    'resmed_ehealth_initmodule_normal_flow.py': 'ding haofeng',
    'resmed_ehealth_updatemodule_robustness_test_ef_a.py': 'ding haofeng',
    'resmed_ehealth_downloadfile_exceptional_flow_a.py': 'Han, Feng',
    'resmed_ehealth_downloadfile_exceptional_flow_c.py': 'Han, Feng',
    'resmed_ehealth_shutdownmodule_nf.py': 'Han, Feng',
    'resmed_ehealth_basic_with_different_sim.py': 'ding haofeng',
    'resmed_ehealth_updateapplication_normalflow.py': 'Han, Feng',
    'resmed_ehealth_download_file_normal_flow.py': 'Han, Feng',
    'resmed_ehealth_updatemodule_nf.py': 'ding haofeng',
    'resmed_ehealth_disableflightmode_normalflow.py': 'ding haofeng',
    'resmed_ehealth_sendhealthdata_af_a.py': 'ding haofeng',
    'resmed_ehealth_shutdownmodule_stresstest.py': 'Han, Feng',
    'resmed_ehealth_sendhealthdata_alternative_flow_a_exceptional_flow_a_b.py': 'ding haofeng',
    'resmed_ehealth_sendhealthdata_stress.py': 'ding haofeng',
    'resmed_ehealth_initmodule_alternative_flow_b_c.py': 'ding haofeng',
    'resmed_ehealth_shut_down_module_normal_flow_stress_test.py': 'Han, Feng',
    'resmed_ehealth_initmodule_alternative_flow_a.py': 'ding haofeng',

    'ebs_alarmdevice_checknetwork_errorhanding_b.py': 'Han, Feng',
    'ebs_alarmdevice_checknetwork_errorhanding_c.py': 'Han, Feng',
    'ebs_alarmdevice_checknetwork_errorhanding_d.py': 'Han, Feng',
    'ebs_alarmdevice_checknetwork_nf.py': 'Han, Feng',
    'ebs_alarmdevice_receiveconfigration_errorhanding_b_c_d.py': 'Han, Feng',
    'ebs_alarmdevice_receiveconfigration_nf.py': 'Han, Feng',
    'ebs_alarmdevice_sendalarm_ef_b.py': 'ding haofeng',
    'ebs_alarmdevice_sendalarm_ef_c.py': 'ding haofeng',
    'ebs_alarmdevice_sendalarm_nf.py': 'ding haofeng',
    'ebs_alarmdevice_sendheartbeat_ef_b.py': 'ding haofeng',
    'ebs_alarmdevice_sendheartbeat_ef_c_d.py': 'ding haofeng',
    'ebs_alarmdevice_sendheartbeat_nf.py': 'ding haofeng',
    'ebs_alarmdevice_sendreport_ef_b.py': 'ding haofeng',
    'ebs_alarmdevice_sendreport_ef_c_d.py': 'ding haofeng',
    'ebs_alarmdevice_sendreport_nf.py': 'ding haofeng',
    'ebs_alarmdevice_updateapplication_b_c_d.py': 'Han, Feng',
    'ebs_alarmdevice_updateapplication_nf.py': 'Han, Feng',

    'trakmate_trackingunit_updatemodule_ef02.py': 'ding haofeng',
    'trakmate_trackingunit_updatemodule_ef01.py': 'ding haofeng',
    'trakmate_trackingunit_updatemoduleIotsuite_nf03.py': 'ding haofeng',
    'trakmate_update_module_nf_1.py': 'ding haofeng',
    'trakmate_update_module_nf_2.py': 'ding haofeng',
    'trakmate_update_application_exceptional_flow.py': 'Liu, Dan',
    'trakmate_update_application_normal_flow.py': 'Liu, Dan',
    'trakmate_switch_sim_profile_normal_flow.py': 'Han, Feng',
    'trakmate_send_trackingdata_loadtest_nf.py': 'ding haofeng',
    'trakmate_send_trackingdata_mqtt_ef.py': 'ding haofeng',
    'trakmate_send_trackingdata_http_ef.py': 'ding haofeng',
    'trakmate_send_trackingdata_tcp_ef.py': 'ding haofeng',
    'trakmate_send_trackingdata_normal_flow.py': 'ding haofeng',
    'trakmate_send_notification_normal_flow.py': 'Liu, Dan',
    'trakmate_send_alert_error_flow.py': 'ding haofeng',
    'trakmate_send_alert_normal_flow.py': 'ding haofeng',
    'trakmate_init_module_error_flow.py': 'ding haofeng',
    'trakmate_init_module_normal_flow.py': 'ding haofeng',
    'trakmate_execute_command_nf.py': 'Han, Feng',
    'trakmate_execute_command_ef.py': 'Han, Feng',
    'trakmate_execute_command_nf_duration.py': 'Han, Feng',
    'trakmate_download_config_normal_flow.py': 'Han, Feng',
    'trakmate_download_config_error_flow.py': 'Liu, Dan'
}


if "__main__" == __name__:
    with open(filepath+readfile, 'r') as f:
        for i in f:
            for keyword in keywords:
                if keyword in i:
                    result.append(i)

    for withoutword in withoutwords:
        for element in result:
            if withoutword in element:
                resultfilter.append(element)

    setfilter = set(resultfilter)
    setresult = set(result)
    lastresult = list(setresult.difference(setfilter))

    exceldata = []
    for i in lastresult:
        for key, value in tname_responsible.items():
            if key in i:
                exceldata.append((i.rstrip(), value))

    with open(filepath + writefile, 'w') as f:
        f.writelines(lastresult)

    # xresult = [x.rstrip() for x in lastresult]
    colName = ['error-info', 'responsible']
    tocsv = pd.DataFrame(columns=colName, data=exceldata)
    tocsv.index += 1
    tocsv.to_csv(filepath+writecsv, encoding='gbk')

