# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107947.001 SissMqtt_basic

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Intention:
    To check if defining Mqtt profiles using SISS command works fine

    Description:
    1) Power on Module
    2) On first SISS profile define mqtt publish profile with only mandatory set of parameters
    3) On second SISS profile define mqtt subscribe profile with only mandatory set of parameters
    4) On third SISS profile define mqtt unsubscribe profile with only mandatory set of parameters
    5) Check if profiles were correctly defined using AT^SISS? command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.publish_addr = "mqtt://147.135.208.186:1"
        test.subscribe_addr = "mqtt://testserver:65535"
        test.unsubscribe_addr = "mqtt://test123"
        test.client_id = "TestModule123"
        test.hc_cont_len = "500"
        test.pub_topic = "test1234"
        test.sub_topicFilter = "test9876"

    def run(test):
        test.log.info("TC0107947.001 SissMqtt_basic")
        test.log.step('1) Power on Module')
        dstl_restart(test.dut)

        test.log.step('2) On first SISS profile define mqtt publish profile with only mandatory '
                      'set of parameters')
        test.mqtt_publish = MqttProfile(test.dut, "0", "1", address=test.publish_addr,
                                        cmd='publish', topic=test.pub_topic,
                                        client_id=test.client_id, hc_cont_len=test.hc_cont_len)
        test.expect(test.mqtt_publish.dstl_get_service().dstl_load_profile())

        test.log.step('3) On second SISS profile define mqtt subscribe profile with only mandatory '
                      'set of parameters')
        test.mqtt_subscribe = MqttProfile(test.dut, "1", "1", address=test.subscribe_addr,
                                        cmd='subscribe', topic_filter=test.sub_topicFilter,
                                        client_id=test.client_id)
        test.expect(test.mqtt_subscribe.dstl_get_service().dstl_load_profile())

        test.log.step('4) On third SISS profile define mqtt unsubscribe profile with only mandatory '
                      'set of parameters')
        test.mqtt_unsubscribe = MqttProfile(test.dut, "2", "1", address=test.unsubscribe_addr,
                                        cmd='unsubscribe', topic_filter=test.sub_topicFilter,
                                        client_id=test.client_id)
        test.expect(test.mqtt_unsubscribe.dstl_get_service().dstl_load_profile())

        test.log.step('5) Check if profiles were correctly defined using AT^SISS? command')
        dstl_check_siss_read_response(test.dut, [test.mqtt_publish, test.mqtt_subscribe,
                                                 test.mqtt_unsubscribe])
    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))


if "__main__" == __name__:
    unicorn.main()