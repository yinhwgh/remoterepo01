# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_android

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        caps = {
            "appPackage": "com.samsung.android.messaging",
            "appActivity": "com.android.mms.ui.ConversationComposer"
        }

        test.driver = test.plugins.android.get_driver(caps)
        test.log.info(test.plugins.android.driver)
        test.expect(test.plugins.android.driver)
        test.plugins.android.logcat_clean()

        test.sleep(2)
        test.log.info("Sending new SMS")
        element = test.driver.find_element_by_id('com.samsung.android.messaging:id/fab')
        element.click()
        test.sleep(2)

        element = test.driver.find_element_by_id('com.samsung.android.messaging:id/recipients_editor_to')
        test.log.info("Entering phone number")
        element.send_keys("+48884816221")
        test.sleep(1)

        msg = "test123"
        element = test.driver.find_element_by_id('com.samsung.android.messaging:id/message_edit_text')
        test.log.info("Entering message: {}".format(msg))
        element.send_keys(msg)
        test.sleep(1)

        element = test.driver.find_element_by_id('com.samsung.android.messaging:id/send_button1')
        test.log.info("Clicking send button")
        element.click()

        test.plugins.android.screenshot("sms.png")

        test.plugins.android.logcat_get_radio_logs()


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
