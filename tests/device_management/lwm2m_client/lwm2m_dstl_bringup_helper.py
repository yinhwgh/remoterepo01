#responsible: thomas.hinze@thalesgroup.com
#location: Berlin

'''
DSTL bring-up helper functions

once the DSTL functions and core extensions are available this file shall be
removed and all usages of these functions in any test cases shall be renamed
from "test_dut_epN_<func>(test, args)" to "test.dut.epN.<func>(args)"
'''


# ---------------------------------------------------------------------------- #

import unicorn
from core import dstl

import requests
import json
from datetime import timezone, datetime, timedelta
import re

import tests.device_management.lwm2m_client.lwm2m_defs as lwm2m

# ---------------------------------------------------------------------------- #

LESHAN_CLIENTS = {}

# ---------------------------------------------------------------------------- #

class LeshanRESTClient:
    """
    Class to call the REST API of the Leshan demo server.
    """

    def __init__(self, baseurl, client=None, proxy=None, server_version='2.0.0'):
        self.proxies = {
            'http': proxy if proxy else ''
        }
        self.baseurl = f'{baseurl}/api'
        self.server_version = server_version
        if client is not None:
            self.client = client
            self.objectspecs = self._get_objectspecs(client)

    def __rest_api__(self, method, rest_url, timeout=None, data=None, headers=None):
        retry_cnt = 0
        retry_max = 3 # TODO: get via test case parameter ?!?

        kwargs = {"proxies" : self.proxies}

        if timeout:
            kwargs["timeout"] = timeout

        if data:
            kwargs["data"] = data

        if headers:
            kwargs["headers"] = headers

        r = requests.request(method, rest_url, **kwargs)

        while retry_cnt < retry_max:
            try:
                return r.json()
            except json.decoder.JSONDecodeError:
                dstl.log.error(f'JSON decode error: {r}')
                if r.status_code in [504]:
                    dstl.log.info(f'retry REST-API request: {retry_cnt + 1}/{retry_max}')
                    retry_cnt += 1
                else:
                    dstl.log.error(f'HTTP status: {r.status_code}')
                    break

        if retry_cnt == retry_max:
            dstl.log.error('connection error - max retries reached')
        # something failed ...
        raise RuntimeError

    def __rest_api_get__(self, rest_url, timeout=None):
        return self.__rest_api__("GET", rest_url, timeout)

    def __rest_api_put__(self, rest_url, timeout=None, data=None, headers=None):
        return self.__rest_api__("PUT", rest_url, timeout=timeout, data=data, headers=headers)

    '''Notes:
        should be public. needed to check if all required objects are presented.
    '''
    def _get_objectspecs(self, client):
        """
        Performs a HTTP GET request to get objects, instance and resource information of registered client.
        E.g. http://127.0.0.1:8080/api/objectspecs/myclient
        :param client: endpoint
        :return: response
        """
        url = f'{self.baseurl}/objectspecs{f"/{client}" if self.server_version == "2.0.0" else ""}'
        response = self.__rest_api_get__(url, timeout=15)
        return response

    def set_client(self, client):
        self.client = client
        self.objectspecs = self._get_objectspecs(client)

    def get_clients(self):
        response = self.__rest_api_get__(f'{self.baseurl}/clients')
        return [client['endpoint'] for client in response]

    '''Notes:
    * later with LWM2M 1.1 we need also a resource instance
    * we need also to read a complete object with all instances or just a complete single instance
        * make some args optional ?!?
    '''
    def read(self, object_name, instance, resource_name):
        """
        Parameters must be provided as strings. In order to built a valid url the numerical ids of
        object_name and resource_name will be read from objectspecs.
        """
        '''TH: using the name from the objspec may not be really portable. if names are changed on the
            server, then all TCs must be adapted. these names should be part of functions that use
            the proper uri.
            current adaptions to allow strings and numbers. might need to be improved.'''
        if isinstance(object_name, (str)):
            resources = next(obj['resourcedefs'] for obj in self.objectspecs if obj['name'] == object_name)
            object_id = next(obj['id'] for obj in self.objectspecs if obj['name'] == object_name)
            resource_id = next(resource['id'] for resource in resources if resource['name'] == resource_name)
        else:
            object_id = object_name
            resource_id = resource_name

        response = self.__rest_api_get__(f'{self.baseurl}/clients/{self.client}/{object_id}/{instance}/{resource_id}')
        return response['content']['value']

    def write(self, object_name, instance, resource_name, value):
        resources = next(obj['resourcedefs'] for obj in self.objectspecs if obj['name'] == object_name)

        object_id = next(obj['id'] for obj in self.objectspecs if obj['name'] == object_name)
        resource_id = next(resource['id'] for resource in resources if resource['name'] == resource_name)

        headers = {'Content-Type': 'application/json'}
        data = {'id': resource_id, 'value': value}
        url = f'{self.baseurl}/clients/{self.client}/{object_id}/{instance}/{resource_id}'

        return self.__rest_api_put__(url, data=json.dumps(data), headers=headers)

# ---------------------------------------------------------------------------- #

class LeshanRestClient(LeshanRESTClient):
    def __init__(self, baseurl, proxy=None, server_version='2.0.0'):
        dstl.log.info(f'create new Leshan server connection: baseurl={baseurl} proxy={proxy}')
        LeshanRESTClient.__init__(self, baseurl, client=None, proxy=proxy, server_version=server_version)
        LESHAN_CLIENTS[baseurl] = self
        self.endpoints = {}

    def get_endpoint(self, device, ep_id):
        try:
            return self.endpoints[f"ep_id_{ep_id}"]
        except KeyError:
            ep_name = __test_dut_ep_get_endpoint_name__(device, ep_id=ep_id)
            ep = LeshanRestEndpoint(ep_name, self)
            self.endpoints[f"ep_id_{ep_id}"] = ep
            return ep

    def is_registered(self, ep_name):
       #dstl.log.info(f'is_registered: ep_name={ep_name} self.proxies={self.proxies} ')
       registered_endpoints = self.get_clients()
       dstl.log.info(f'registered_endpoints={registered_endpoints} ep_name={ep_name}')
       return ep_name in registered_endpoints


    # not supported by leshan ?!?
    #def read_object(self, ep_name, obj_id, obj_inst):
    #    r = requests.get(f'{self.baseurl}/clients/{ep_name}/{obj_id}/{obj_inst}', proxies=self.proxies)
    #    
    #    dstl.log.info(f'r={r}')
    #    response = r.json()
    #
    #    dstl.log.info(f'response={response}')
    #
    #    return response['content']['value']

    '''
        res_inst is required latest with LWM2M 1.1.
    '''
    def read_resource(self, ep_name, obj_id, obj_inst, res_id, res_inst):
        response = self.__rest_api_get__(f'{self.baseurl}/clients/{ep_name}/{obj_id}/{obj_inst}/{res_id}')
        return response['content']['value']

    '''
        res_inst is required latest with LWM2M 1.1.
    '''
    def write_resource(self, ep_name, obj_id, obj_inst, res_id, res_inst, value):
        #dstl.log.info(f'ep_name={ep_name} obj_id={obj_id} obj_inst={obj_inst} res_id={res_id}')
        headers = {'Content-Type': 'application/json'}
        data = {'id': res_id, 'value': value}
        url = f'{self.baseurl}/clients/{ep_name}/{obj_id}/{obj_inst}/{res_id}'

        data=json.dumps(data)
        response = self.__rest_api_put__(url, data=data, headers=headers)

        return response

    def exec_resource(self, ep_name, obj_id, obj_inst, res_id, res_inst):
        return False

    def observe_resource(self, ep_name, obj_id, obj_inst, res_id, res_inst):
        return False

# ---------------------------------------------------------------------------- #

class LeshanRestEndpoint(object):
    def __init__(self, ep_name, server):
        dstl.log.info('create new Leshan Endpoint')
        self.ep_name = ep_name
        self.server = server

    def is_registered(self):
        return self.server.is_registered(self.ep_name)

    def read_object(self, obj_id, obj_inst):
        return self.server.read_object(self.ep_name, obj_id, obj_inst)

    def read_resource(self, obj_id, obj_inst, res_id, res_inst=None):
        value = self.server.read_resource(self.ep_name, obj_id, obj_inst, res_id, res_inst)

        if res_inst:
            dstl.log.info(f'read resource /{obj_id}/{obj_inst}/{res_id}/{res_inst}: {value}')
        else:
            dstl.log.info(f'read resource /{obj_id}/{obj_inst}/{res_id}: {value}')

        return value


    def write_resource(self, obj_id, obj_inst, res_id, value, res_inst=None):
        if res_inst:
            dstl.log.info(f'write resource /{obj_id}/{obj_inst}/{res_id}/{res_inst}: {value}')
        else:
            dstl.log.info(f'write resource /{obj_id}/{obj_inst}/{res_id}: {value}')

        return self.server.write_resource(self.ep_name, obj_id, obj_inst, res_id, res_inst, value)

    def exec_resource(self, obj_id, obj_inst, res_id, res_inst=None):
        return self.server.exec_resource(self.ep_name, obj_id, obj_inst, res_id, res_inst)

    def observe_resource(self, obj_id, obj_inst, res_id, res_inst=None):
        pass

# ---------------------------------------------------------------------------- #

def __test_dut_ep_get_server__(device, ep_id, server_id):
    if server_id is None:
        server_id = 1

    try:
        # get server (webapi) from test parameter
        server = getattr(dstl.test, f'lwm2m_ep{ep_id}_server{server_id}')
        server_url = getattr(dstl.test, f'{server}_url_web')
    except AttributeError:
        dstl.fail(f'missing endpoint server parameter: lwm2m_ep{ep_id}_server{server_id}')

    try:
        return LESHAN_CLIENTS[server_url]
    except KeyError:
        # get proxy from test parameter
        try:
            proxy = getattr(dstl.test, f'{server}_proxy')
        except AttributeError:
            proxy = None

        dstl.log.debug(f'proxy for {server}: {proxy}')

        return LeshanRestClient(server_url, proxy=proxy)

# ---------------------------------------------------------------------------- #

def __test_dut_ep_get_endpoint_type__(device, ep_id):
    try:
        return "attus"
        #return device.get_attr(f'lwm2m_ep{ep_id}_client')
    except AttributeError:
        device.fail(f'missing endpoint client type: lwm2m_ep{ep_id}_client')

# ---------------------------------------------------------------------------- #

def __test_dut_ep_get_endpoint_name__(device, ep_id):
    # TODO: avoid to read IMEI each and every time
    imei = device.dstl_get_imei()

    client_type = __test_dut_ep_get_endpoint_type__(device, ep_id)
    if client_type == lwm2m.ENDPOINT_ATT:
        return f"urn:imei:{imei}"

        # TODO: use proper ep name for AT&T
        #msisdn = device.get_msidsn()
        #return f"urn-imei-msisdn:{imei}-{msisdn}"

    elif client_type == lwm2m.ENDPOINT_VZW:
        # TODO
        pass

    else:
        return f"urn-imei:{imei}"

# ---------------------------------------------------------------------------- #

def __test_dut_ep_get_endpoint__(device, ep_id, server_id=None):
    server = __test_dut_ep_get_server__(device, ep_id=ep_id, server_id=server_id)

    return server.get_endpoint(device=device, ep_id=ep_id)

# ---------------------------------------------------------------------------- #

def __test_dut_ep_start_test_context__(device, ep_id):
    dstl.log.info("start context manually until auto-bearer bring up is implemented")
    try:
        cid = 1
        # TODO: get from parameter
        #cid = test.get_attr(f"lwm2m_ep{ep_id}_test_cid")
    except AttributeError:
        dstl.log.info(f"no test CID defined for EP#{ep_id}")
        return

    res = device.at1.send_and_verify(f"AT^SICA={cid}, 1", "*.OK")
    
    # TODO check result
    #dstl.expect(res is True, critical=True)

# ---------------------------------------------------------------------------- #

def __test_dut_ep_start_client__(device, ep_id):
    client_type = __test_dut_ep_get_endpoint_type__(device, ep_id)

    if client_type == lwm2m.ENDPOINT_ATT:
        client = "attus"
    elif client_type == lwm2m.ENDPOINT_VZW:
        client = "verizonus"
    elif client_type == lwm2m.ENDPOINT_MODS:
        client = "mods"
    else:
        dstl.fail(f"unknown client type: {client_type}")

    __test_dut_ep_start_test_context__(device, ep_id)

    return device.at1.send_and_verify(f"AT^SNLWM2M=\"act\",\"{client}\",\"start\"", ".*OK")

# ---------------------------------------------------------------------------- #

def __test_dut_ep_wait_for_registration__(device, ep_id, server_id, timeout, critical):
    dstl.log.info('wait_for_registration')
    ep = __test_dut_ep_get_endpoint__(device, ep_id=ep_id, server_id=server_id)

    poll_time = 1

    # use: dstl.attempt(...)

    try:
        while timeout > 0:
            if ep.is_registered():
                dstl.log.info(f'endpoint #{ep_id} is registered')
                return True

            dstl.sleep(poll_time)
            timeout -= poll_time

        res = ep.is_registered()
    except RuntimeError:
        dstl.log.error('communication error with server')
        res = None

    dstl.expect(res is True, critical=critical)

    return res

# ---------------------------------------------------------------------------- #

def __test_dut_ep_read_resource__(device, ep_id, obj_id, res_id, obj_inst=0, res_inst=None, server_id=None):
    ep = __test_dut_ep_get_endpoint__(device, ep_id=ep_id, server_id=server_id)
    return ep.read_resource(obj_id, obj_inst, res_id, res_inst)

# ---------------------------------------------------------------------------- #

def __test_dut_ep_write_resource__(device, ep_id, obj_id, res_id, value, obj_inst=0, res_inst=None, server_id=None):
    ep = __test_dut_ep_get_endpoint__(device, ep_id=ep_id, server_id=server_id)
    return ep.write_resource(obj_id, obj_inst, res_id, res_inst=res_inst, value=value)

# ---------------------------------------------------------------------------- #

def __test_dut_ep_exec_resource__(device, ep_id, obj_id, res_id, obj_inst=0, res_inst=None, server_id=None):
    ep = __test_dut_ep_get_endpoint__(device, ep_id=ep_id, server_id=server_id)
    return ep.exec_resource(obj_id, obj_inst, res_id, res_inst)

# ---------------------------------------------------------------------------- #

def __test_dut_ep_lwm2m_server_configure_psk__(device, ep_id, psk, psk_identity=None, server_id=None):
    ep = __test_dut_ep_get_endpoint__(device, ep_id=ep_id, server_id=server_id)
    return ep.lwm2m_server_configure_psk(psk, psk_identity=psk_identity)

# ============================================================================ #
#dstl_fn(device, ....):
#    dstl.log.info(...)
#    device.ep1.get_imei() # default server: #0
#    device.ep1.get_imei(server_id=1) # use server 1 instead

#cfg:
# lwm2m_ep1_server1="mods1.server"
# lwm2m_ep1_server2="mods2.server"
# lwm2m_ep2_server1="att.server"
#    device.ep2.get_imei(server_id=1) # use server 1 instead
#    device.ep2.get_imei(server_id="lwm2m_ep2_server1") # use server 1 instead

# lwm2m_server1="mods1.server"
# lwm2m_server2="mods2.server"
# lwm2m_server3="att.server"
#    device.ep2.get_imei(lwm2m_server=3) # use server 1 instead

# lwm2m_server_ep1_default="..."
# lwm2m_server_att="att.server"
#    device.ep2.get_imei(server_id="lwm2m_server_att") # use server 1 instead -> common understanding for best approach

#lwm2m_server_1 = lwm2m_server_att
#lwm2m_server_att ="att.server"
#    device.ep2.get_imei(server_id="lwm2m_server_1") # use server 1 instead -> common understanding for best approach

# epN -> LWM2M server #1
#     -> LWM2M server #2 ... 65535
#     -> Bootstrap server
#     -> FOTA server #1 , #2 , ...

# ---------------------------------------------------------------------------- #

def test_dut_dstl_get_model(device):
        device.at1.send_and_verify("AT+CGMM", ".*OK.*")
        response_list = list(filter(None, device.at1.last_response.split('\r\n')))
        return response_list[response_list.index('OK') - 1]  # The last item is 'OK', the penultimate should be value

# ---------------------------------------------------------------------------- #

def test_dut_dstl_get_fw_revision(device):        
        device.at1.send_and_verify("AT+CGMR", ".*OK.*")
        response_list = list(filter(None, device.at1.last_response.split('\r\n')))
        cgmr_rsp = response_list[response_list.index('OK') - 1]  # The last item is 'OK', the penultimate should be value
        return cgmr_rsp.replace('REVISION ', '')

# ---------------------------------------------------------------------------- #

# TODO: see dstl_detect for maybe existing DSTL function(s)
def test_dut_dstl_get_sw_revision(device):        
        device.at1.send_and_verify("ATI1", ".*OK.*")
        response_list = list(filter(None, device.at1.last_response.split('\r\n')))
        cgmr_rsp = response_list[response_list.index('OK') - 1]  # The last item is 'OK', the penultimate should be value
        return cgmr_rsp.replace('A-REVISION ', '')

def test_dut_dstl_get_sw_version_number(device):        
        device.at1.send_and_verify("ATI176", ".*OK.*")
        response_list = list(filter(None, device.at1.last_response.split('\r\n')))
        cgmr_rsp = response_list[response_list.index('OK') - 1]  # The last item is 'OK', the penultimate should be value
        return cgmr_rsp.rsplit('.', 1)[1]

# ---------------------------------------------------------------------------- #

# see dstl_detect
def test_dut_get_time(device):        
        device.at1.send_and_verify("AT+CCLK?", ".*OK.*")
        response_list = list(filter(None, device.at1.last_response.split('\r\n')))
        cclk_rsp = response_list[response_list.index('OK') - 1]  # The last item is 'OK', the penultimate should be value
        date_time_str = cclk_rsp.replace('+CCLK: ', '')

        # depending on AT+CTZU setting the time may contain TZ info or not
        tz = None

        match = re.match(".*([\+-])([0-9][0-9])", date_time_str)
        if match:
            sign = match.group(1)
            timezone_h = match.group(2)
            delta_hours = int(timezone_h)
            #dstl.log.info(f'timezone: {sign} {delta_hours}')
            date_time_str = date_time_str.replace(sign + timezone_h, '')

            tz_delta = timedelta(hours=delta_hours)

            if sign == '-':
                tz_delta *= -1

            #dstl.log.info(f'tz_delta: {tz_delta}')
            tz = timezone(tz_delta)
        else:
            tz = timezone.utc

        #dstl.log.info(f'tz: {tz}')

        dt = datetime.strptime(date_time_str, '"%y/%m/%d,%H:%M:%S"')
        #dstl.log.info(f'dt: {dt}')

        if tz:
            #dstl.log.info(f'set tz: {tz}')
            dt = dt.replace(tzinfo=tz)
            #dstl.log.info(f'dt: {dt.isoformat()}')

        return dt

# ---------------------------------------------------------------------------- #

'''Get expected total memory values for each product'''
#@Viper1
def test_dut_ep1_dstl_get_defined_lwm2m_memory_total_kB(device):
    return 10754

# ---------------------------------------------------------------------------- #

#@default (Javelin)
#@Serval
#@Cougar
def test_dut_ep1_dstl_get_defined_lwm2m_binding_modes(device):
    # TODO: return expected string or list of "enums" ???
    return "UQS"

def test_dut_ep1_dstl_get_defined_lwm2m_fota_protocols(device):
    return "TODO"

def test_dut_ep1_dstl_get_defined_lwm2m_delviery_methods(device):
    return "TODO"

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_endpoint_type(device):
    return __test_dut_ep_get_endpoint_type__(device, ep_id=1)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_set_test_env(device):
    test.dut.set_context(test.lwm2m_ep1_test_cid,
                         test.lwm2m_ep1_test_apn,
                         test.lwm2m_ep1_test_apn_type,
                         test.lwm2m_ep1_test_apn_user,
                         test.lwm2m_ep1_test_apn_secret)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_start_client(device):
    return __test_dut_ep_start_client__(device, ep_id=1)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_wait_for_registration(device, timeout=5, critical=False, server_id=None):
    dstl.log.debug('wait for registration: ep #1')
    return __test_dut_ep_wait_for_registration__(device, ep_id=1,
                                                 timeout=timeout,
                                                 critical=critical,
                                                 server_id=server_id)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_read_object(device, obj_id, obj_inst=None, server_id=None):
    ep = __test_dut_ep_get_endpoint__(device, ep_id=1, server_id=server_id)
    return ep.read_object(obj_id, obj_inst)

# ---------------------------------------------------------------------------- #
#test.dut.ep1.dstl_get_manufacturer
def test_dut_ep1_dstl_get_manufacturer(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_MANUFACTURER)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_model(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_MODEL)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_imei(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_SERIAL_NO)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_fw_revision(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_FW_VERSION)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_device_type(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_DEVICE_TYPE)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_hw_revision(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_HW_REVISION)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_sw_revision(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_SW_REVISION)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_binding_modes(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_BINDING_MODES)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_time(device, server_id=None):
    '''Get time from LWM2M server

        returns:
            datetime object
                if proper time string was received from server

            None
                if invalid time received by server or request to server failed
    '''
    try:
        date_time_str = __test_dut_ep_read_resource__(device, ep_id=1,
                                                    server_id=server_id,
                                                    obj_id=lwm2m.OBJ_DEVICE,
                                                    res_id=lwm2m.RES_DEVICE_CURRENT_TIME)
    except RuntimeError:
        dstl.log.error('communication error with server')
        return False

    result = date_time_str.rsplit(":", 1)
    date_time_str = "".join(result) 
    #dstl.log.info(f"date_time_str={date_time_str} (removed colon in TZ)")
    try:
        return datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        # something is wrong with the time sent by the LWM2M server
        dstl.log.error(f'invalid time sent by server: {date_time_str}')
        return False

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_set_time(device, new_time: datetime, server_id=None):
    datetime_str = new_time.strftime("%Y-%m-%dT%H:%M:%S%z")
    # Leshan server expect time with colon in TZ offset
    datetime_str = datetime_str[:-2] + ':' + datetime_str[-2:]
    #dstl.log.info(f"dstl-lwm2m: set_time: date_time_str={datetime_str}")
    return __test_dut_ep_write_resource__(device, ep_id=1,
                                      server_id=server_id,
                                      obj_id=lwm2m.OBJ_DEVICE,
                                      res_id=lwm2m.RES_DEVICE_CURRENT_TIME,
                                      value=datetime_str)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_reset(device, server_id=None):
    return __test_dut_ep_exec_resource__(device, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_DEVICE,
                                         res_id=lwm2m.RES_DEVICE_REBOOT)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_free_memory(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_DEVICE,
                                         res_id=lwm2m.RES_DEVICE_MEMORY_FREE)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_total_memory(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_DEVICE,
                                         res_id=lwm2m.RES_DEVICE_MEMORY_TOTAL)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_factory_reset(device, server_id=None):
    return __test_dut_ep_exec_resource__(device, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_DEVICE,
                                         res_id=lwm2m.RES_DEVICE_FACTORY_RESET)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_supported_fota_protocols(test, server_id=None):
    return __test_dut_ep_read_resource__(test, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_FOTA,
                                         res_id=lwm2m.RES_FOTA_PROTOCOL_SUPPORT)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_supported_delivery_methods(test, server_id=None):
    return __test_dut_ep_read_resource__(test, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_FOTA,
                                         res_id=lwm2m.RES_FOTA_DELIVERY_METHOD)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_fota_set_uri(test, fota_package_uri, server_id=None):
    return __test_dut_ep_write_resource__(test, ep_id=1,
                                          server_id=server_id,
                                          obj_id=lwm2m.OBJ_FOTA,
                                          res_id=lwm2m.RES_FOTA_PACKAGE_URI,
                                          value=fota_package_uri)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_fota_reset(test, server_id=None):
    return test_dut_ep1_fota_set_uri(test, fota_package_uri="",
                                     server_id=server_id)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_fota_get_state(test, server_id=None):
    return __test_dut_ep_read_resource__(test, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_FOTA,
                                         res_id=lwm2m.RES_FOTA_STATE)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_fota_get_result(test, server_id=None):
    return __test_dut_ep_read_resource__(test, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_FOTA,
                                         res_id=lwm2m.RES_FOTA_UPDATE_RESULT)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_start_update(test, server_id=None):
    return __test_dut_ep_exec_resource__(test, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_FOTA,
                                         res_id=lwm2m.RES_FOTA_UPDATE)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_fota_push_fw_file(test, fota_fw_file, offset=None, length=None, server_id=None):
    # file = open(fota_fw_file)
    # data = file.read(offset, length)
    data = None
    return __test_dut_ep_write_resource__(test, ep_id=1,
                                          server_id=server_id,
                                          obj_id=lwm2m.OBJ_FOTA,
                                          res_id=lwm2m.RES_FOTA_PACKAGE,
                                          value=data)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_get_lwm2m_server_lifetime(device, server_id=None):
    return __test_dut_ep_read_resource__(device, ep_id=1,
                                         server_id=server_id,
                                         obj_id=lwm2m.OBJ_LWM2M_SERVER,
                                         res_id=lwm2m.RES_LWM2M_SERVER_LIFETIME)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_set_lwm2m_server_lifetime(device, lwm2m_server_lifetime, server_id=None):
    return __test_dut_ep_write_resource__(device, ep_id=1,
                                          server_id=server_id,
                                          obj_id=lwm2m.OBJ_LWM2M_SERVER,
                                          res_id=lwm2m.RES_LWM2M_SERVER_LIFETIME,
                                          value=lwm2m_server_lifetime)

# ---------------------------------------------------------------------------- #

def test_dut_ep1_dstl_lwm2m_server_configure_psk(device, psk, psk_identity=None, server_id=None):
    pass

# ---------------------------------------------------------------------------- #

def __test_dut_ep_dstl_configure_psk__(device, ep_id, psk, psk_identity=None, server_id=None):
    # TODO: get CSCS setting -> GSM or UCS2
    if isinstance(psk, (str)):
        psk_str_gsm = test.__to_gsm_string__(psk)
        psk_str_ucs2 = test.__to_ucs2_string__(psk)
    elif isinstance(psk, (bytearray)):
        psk_str_ucs2 = test.__to_ucs2_string__(psk)
        # TODO: set CSCS setting -> UCS2

    device.at1.send_and_verify(f"AT^SNLWM2M=\"cfg\",\"{client}\",\"/{lwm2m.OBJ_SECURITY}/{server_id}/{lwm2m.RES_SECURITY_PUBLIC_KEY_OR_IDENTITY}\",\"{psk_identity}\"", ".*OK")
    device.at1.send_and_verify(f"AT^SNLWM2M=\"cfg\",\"{client}\",\"/{lwm2m.OBJ_SECURITY}/{server_id}/{lwm2m.RES_SECURITY_SECRET_KEY}\",\"{psk}\"", ".*OK")

def test_dut_ep1_dstl_configure_psk(device, psk, psk_identity=None, server_id=None):
    __test_dut_ep_dstl_configure_psk__(device, ep_id=1, server_id=server_id, psk=psk, psk_identity=psk_identity)

# ---------------------------------------------------------------------------- #

def test_dut_ep_dstl_configure_security_mode(device, ep_id, security_mode, server_id=None):
    device.at1.send_and_verify(f"AT^SNLWM2M=\"cfg\",\"{client}\",\"/{lwm2m.OBJ_SECURITY}/{server_id}/{lwm2m.RES_SECURITY_MODE}\",\"{security_mode}\"", ".*OK")

def test_dut_ep1_dstl_configure_security_mode(device, security_mode, server_id=None):
    __test_dut_ep_dstl_configure_security_mode__(device, ep_id=1, server_id=server_id, security_mode=security_mode)
