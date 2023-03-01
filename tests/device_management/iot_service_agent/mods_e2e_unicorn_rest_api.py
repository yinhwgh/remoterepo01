# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin

import requests
from requests.auth import HTTPBasicAuth
import json
import tests.device_management.iot_service_agent.mods_e2e_unicorn_server_config as server_config
from core import dstl

AUTH = HTTPBasicAuth(server_config.USER, server_config.PASSWORD)
HEADERS = {'Accept': 'application/json'}
PROXIES = server_config.PROXIES


# UTILITY FUNCTIONS ################################################################################
def log_http_details(r):
    dstl.log.info(f'{r.request.method} {r.request.url}')
    dstl.log.info(f'URL access status: {r.status_code}')


def log_body(body):
    dstl.log.info(f'RESPONSE BODY: \n {json.dumps(body, indent=4, sort_keys=True)}')


# DEVICE API #######################################################################################
def get_devices():
    url = server_config.DEVICE_API
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_device_with_imei(imei):
    url = f'{server_config.DEVICE_API}/with/imei/{imei}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def create_device(imei, label, msisdn=None, iccid=None):
    url = server_config.DEVICE_API
    payload = {
        "imei": imei,
        "label": label,
    }
    r = requests.post(url, verify=True,
                      headers=HEADERS, auth=AUTH, proxies=PROXIES, json=payload)
    log_http_details(r)

    return r


def get_device(id):
    url = f'{server_config.DEVICE_API}/{id}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_device_long(id):
    url = f'{server_config.DEVICE_API}/{id}?view=full'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def delete_device(id):
    url = f'{server_config.DEVICE_API}/{id}'
    r = requests.delete(url, verify=True,
                        headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_device_id(devices, imei):
    try:
        return [x['id'] for x in devices if x['imei'] == imei][0]
    except IndexError:
        dstl.log.info(f'There is no device with imei {imei} on MODS available')


def assign_fallback_rule(device_id, rule_name):
    url = f'{server_config.DEVICE_API}/{device_id}/fallbackConnectivityProvisionRule/{rule_name}'
    r = requests.put(url, verify=True,
                     headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def assign_provision_rule(device_id, rule_name):
    url = f'{server_config.DEVICE_API}/{device_id}/initialConnectivityProvisionRule/{rule_name}'
    r = requests.put(url, verify=True,
                     headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def assign_parameter_read_mode(device_id, mode):
    url = f'{server_config.DEVICE_API}/{device_id}/parameterReadMode/{mode}'
    r = requests.put(url, verify=True,
                     headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


# RULES API ########################################################################################
def get_rules():
    url = f'{server_config.RULES_API}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_rule(id):
    url = f'{server_config.RULES_API}/{id}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def create_rule(name, type, description, preferredOperator, preferredIssuer):
    url = f'{server_config.RULES_API}/{type}'

    payload = {
        "name": name,
        "description": description,
        "preferredOperator": preferredOperator,
        "preferredIssuer": preferredIssuer
    }
    r = requests.post(url, verify=True,
                      headers=HEADERS, auth=AUTH, proxies=PROXIES, json=payload)
    log_http_details(r)

    return r


def delete_rule(id):
    url = f'{server_config.RULES_API}/{id}'
    r = requests.delete(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def find_rule(rules, rule_name):
    try:
        return [rule for rule in rules if rule['name'] == rule_name][0]
    except IndexError:
        dstl.log.error(f"No rule with name {rule_name} found")
        return None


# SUBSCRIPTION API #################################################################################
def get_subscriptions():
    url = f'{server_config.SUBSCRIPTIONS_API}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_subscription(id):
    url = f'{server_config.SUBSCRIPTIONS_API}/{id}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def find_subscriptions_by_field(subscriptions, field_name, field_value):
    return [subscription for subscription in subscriptions if
            field_name in subscription and
            subscription[field_name] == field_value]


def find_subscriptions_without_imei(subscriptions):
    return [subscription for subscription in subscriptions if
            'imei' not in subscription]


def get_active_subscription_by_imei(subscriptions, imei):
    return [subscription for subscription in subscriptions if
            subscription['status'] == 'activated' and 'imei' in subscription and subscription[
                'imei'] == imei][0]


def find_all_not_activated_iccid_by_imei(subscriptions, imei):
    iccid = []
    for i in subscriptions:
        if not i['status'] == 'available' and 'imei' in i.keys():
            if imei in i['imei']:
                dstl.log.info("found element: " + str(i))
                iccid.append(i['iccid'])

    dstl.log.info("Here are the found iccids which belong to your imei: " + imei + " " + str(iccid))
    return iccid


def find_all_iccids_by_imei(subscriptions, imei):
    iccid = []
    for i in subscriptions:
        if 'imei' in i.keys():
            if imei in i['imei']:
                dstl.log.info("found element: " + str(i))
                iccid.append(i['iccid'])

    dstl.log.info("Here are the found iccids which belong to your imei: " + imei + " " + str(iccid))
    return iccid


def get_all_iccids(subscriptions):
    return [subscription['iccid'] for subscription in subscriptions]


def get_all_iccids_and_subscriptions_ids(subscriptions):
    iccids_and_subscription_id = []
    for i in subscriptions:
        dstl.log.info("found element: " + str(i['iccid']) + " " + str(i['id']))
        iccids_and_subscription_id.append([i['iccid'], i['id']])

    return iccids_and_subscription_id


def get_all_subscription_ids_by_imei(subscriptions, imei):
    ids = []
    for i in subscriptions:
        if 'imei' in i.keys():
            if imei in i['imei']:
                dstl.log.info("found element: " + str(i))
                ids.append(i['id'])

    dstl.log.info(
        "Here are the found subscription_ids which belong to your imei: " + imei + " " + str(ids))
    return ids


def get_all_not_activated_subscription_ids_by_imei(subscriptions, imei):
    ids = []
    for i in subscriptions:
        if not i['status'] == 'available' and i['imei']:
            if imei in i['imei']:
                dstl.log.info("found element: " + str(i))
                ids.append(i['id'])

    dstl.log.info("Here are the found iccids which belong to your imei: " + imei + " " + str(ids))
    return ids


def get_subscription_state_by_imei(subscriptions, imei):
    return [subscription['status'] for subscription in subscriptions if
            'imei' in subscription and subscription['imei'] == imei][0]


def create_subscription(iccid, apn_profile_id):
    url = f'{server_config.SUBSCRIPTIONS_API}/iccids'

    payload = {
        "iccid": iccid,
        "apnProfileId": apn_profile_id
    }
    r = requests.post(url, verify=True,
                      headers=HEADERS, auth=AUTH, proxies=PROXIES, json=payload)
    log_http_details(r)

    return r


def delete_subscription(id):
    url = f'{server_config.SUBSCRIPTIONS_API}/{id}'
    r = requests.delete(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def drop_subscription(id):
    url = f'{server_config.SUBSCRIPTIONS_API}/{id}:drop'
    r = requests.delete(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


# JOB API ##########################################################################################
def get_jobs():
    url = f'{server_config.JOB_API}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_job(id):
    url = f'{server_config.JOB_API}/{id}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_job_targets(id):
    url = f'{server_config.JOB_API}/{id}/targets'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def find_job_target(job_targets, target_id):
    try:
        return [target for target in job_targets if target['deviceId'] == target_id][0]
    except IndexError:
        return None


def create_connectivity_switch(name, description, pool_id):
    url = f'{server_config.JOB_API}/connectivitySwitch'

    payload = {
        "name": name,
        "description": description,
        "targetPoolId": pool_id
    }
    r = requests.post(url, verify=True,
                      headers=HEADERS, auth=AUTH, proxies=PROXIES, json=payload)
    log_http_details(r)

    return r


def create_job_target(job_id, device_id):
    url = f'{server_config.JOB_API}/{job_id}/targets'

    payload = {
        "deviceId": device_id
    }
    r = requests.post(url, verify=True,
                      headers=HEADERS, auth=AUTH, proxies=PROXIES, json=payload)
    log_http_details(r)

    return r


def schedule_job(job_id, schedule_from, schedule_to):
    url = f'{server_config.JOB_API}/{job_id}:schedule'

    payload = {
        "from": schedule_from,
        "to": schedule_to
    }
    r = requests.put(url, verify=True,
                     headers=HEADERS, auth=AUTH, proxies=PROXIES, json=payload)
    log_http_details(r)

    return r


def get_jobs_since_time(imei, job_type, time):
    url = (
        f'{server_config.JOB_API}/targets/search?size=1000&imei={imei}&jobType={job_type}&'
        f'statusTime>={time}&sort=statusTime'
    )
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r

def abort_job(job_id):
    url = f'{server_config.JOB_API}/{job_id}:abort'

    r = requests.put(url, verify=True,headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r

# APN API ##########################################################################################
def get_apn_profiles():
    url = f'{server_config.APN_PROFILES_API}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_apn_profile(id):
    url = f'{server_config.APN_PROFILES_API}/{id}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def find_apn_profile_id(apn_profiles, profile_name):
    try:
        return [apn_profile['id'] for apn_profile in apn_profiles
                if apn_profile['profileName'] == profile_name][0]
    except IndexError:
        dstl.log.error(f'No apn profile found with profile name {profile_name}')


def create_apn_profile(profile_name, apn, authentication_type, user_name, secret, pdn_type):
    url = server_config.APN_PROFILES_API

    payload = {
        "profileName": profile_name,
        "apn": apn,
        "authenticationType": authentication_type,
        "userName": user_name,
        "secret": secret,
        "pdnType": pdn_type,
    }
    r = requests.post(url, verify=True,
                      headers=HEADERS, auth=AUTH, proxies=PROXIES, json=payload)
    log_http_details(r)

    return r


def delete_apn_profile(id):
    url = f'{server_config.APN_PROFILES_API}/{id}'
    r = requests.delete(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


# PACKAGE MANAGEMENT API ###########################################################################
def get_firmwares():
    url = f'{server_config.PACKAGE_MANAGEMENT_API}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r


def get_firmware(id):
    url = f'{server_config.PACKAGE_MANAGEMENT_API}/{id}'
    r = requests.get(url, verify=True, headers=HEADERS, auth=AUTH, proxies=PROXIES)
    log_http_details(r)

    return r
