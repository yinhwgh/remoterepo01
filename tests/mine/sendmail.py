import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time

filepath = r'C:\Users\T0259343\Desktop\test'
readfile = r'\test01yhw_test.log'
keywords = ['not send SYSSTART']
withoutwords = ['Start Error', 'force_abnormal_flow']
result = []


class Mail:
    def __init__(self):
        # 第三方 SMTP 服务

        self.mail_host = "smtp.qq.com"  # 设置服务器:这个是qq邮箱服务器，直接复制就可以
        self.mail_pass = "amcoirmkzlahcaie"  # 刚才我们获取的授权码
        self.sender = '271234052@qq.com'  # 你的邮箱地址
        self.receivers = ['hongwei.yin@thalesgroup.com', 'dongmei.guo@thalesgroup.com']  # 收件人的邮箱地址，可设置为你的QQ邮箱或者其他邮箱，可多个

    def send(self, content):

        content = content
        message = MIMEText(content, 'plain', 'utf-8')

        message['From'] = Header("hi～我是实时监控小程序", 'utf-8')
        message['To'] = Header("dongmei", 'utf-8')

        subject = 'bulk tester report'  # 发送的主题，可自由填写
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP_SSL(self.mail_host, 465)
            smtpObj.login(self.sender, self.mail_pass)
            smtpObj.sendmail(self.sender, self.receivers, message.as_string())
            smtpObj.quit()
            print('邮件发送成功')
        except smtplib.SMTPException as e:
            print('邮件发送失败')


if __name__ == "__main__":
    mail = Mail()
    for lp in range(6):
        with open(filepath + readfile, 'r') as f:
            for i in f:
                for keyword in keywords:
                    if keyword in i:
                        result.append(i)
        resstr = ''.join(result)
        print(result)
        result.clear()
        print(f'***this is {lp+1} loop***')
        # if resstr:
        #     mail.send(resstr)
        # time.sleep(3600)
