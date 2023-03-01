# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian

'''
Aux function for use case script
'''


def toggle_off_rts(test):
    test.dut.at1.connection.setRTS(False)
    test.sleep(1)
    test.log.info(f"Turn off RTS line,state: {test.dut.at1.connection.rts}")


def toggle_on_rts(test):
    test.dut.at1.connection.setRTS(True)
    test.sleep(1)
    test.log.info(f"Turn on RTS line, state: {test.dut.at1.connection.rts}")


def step_with_error_handle(max_retry, step_if_error):
    def wrapper(func):
        def retry(test, force_abnormal_flow, *args, **kw):
            if force_abnormal_flow:
                toggle_off_rts(test)
            i = 0
            while i < max_retry:
                test.log.info(f'Execute step: {func.__name__}, the {i + 1} time')
                result = func(test, force_abnormal_flow, *args, **kw)
                if result:
                    return True
                else:
                    i += 1
                    test.sleep(2)
            toggle_on_rts(test)
            step_if_error(test)

        return retry

    return wrapper


def generate_hash_file(test, file_name):
    dir = '/home/download/'
    cmd = f'openssl dgst -sha256 {dir + file_name}'
    test.ssh_server.send_and_verify('pwd')
    result = test.ssh_server.send_and_receive(f'{cmd}')
    crc = 0
    for i in range(2):
        if 'SHA256' in result:
            crc = result.split('=')[1].strip()
            break
        else:
            i += 1
    if crc:
        test.log.info(f'Hash Value is {crc}')
        test.ssh_server.send_and_verify(f'sudo echo {crc} > {dir}crc_value')
    else:
        test.log.error('Generate hash value fail')

    return crc
