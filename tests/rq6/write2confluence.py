from selenium import webdriver
import time


filepath = r'C:\Users\T0259343\Desktop\test'
readfile = r'\test01yhw_test.log'
keywords = ['not send SYSSTART']
result = []

if __name__ == "__main__":
    chrome_options = webdriver.ChromeOptions()
    # 使用headless无界面浏览器模式
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    # 启动浏览器，获取网页源代码
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.implicitly_wait(30)
    mainUrl = "https://confluence.gemalto.com/display/M2MRDVAL/FSD+Alert"
    browser.get(mainUrl)
    username = browser.find_element_by_id('userNameInput')
    username.send_keys(r'gemalto\t0259343')
    password = browser.find_element_by_id('passwordInput')
    password.send_keys(r'gemalto.123')
    submit = browser.find_element_by_id('submitButton')
    submit.submit()
    for i in range(1):
        comment = browser.find_element_by_xpath('//*[@id="comments-section"]/div[2]/div/div/form/div/span')
        comment.click()
        browser.switch_to.frame("wysiwygTextarea_ifr")
        paragraph = browser.find_element_by_xpath('//*[@id="tinymce"]/p')

        with open(filepath + readfile, 'r') as f:
            for i in f:
                for keyword in keywords:
                    if keyword in i:
                        result.append(i)
        resstr = ''.join(result)
        print(result)
        result.clear()

        if resstr:
            paragraph.send_keys(resstr)
            browser.switch_to.parent_frame()
            savebutton = browser.find_element_by_id('rte-button-publish')
            savebutton.submit()
            time.sleep(60)
    browser.quit()


    # paragraph.send_keys(f'let it go {time.time()}')
    # browser.switch_to.parent_frame()
    # savebutton = browser.find_element_by_id('rte-button-publish')
    # savebutton.submit()
    # browser.quit()