# 使用ETAS软件进行报文录制

import time
from datetime import datetime
import can
from can.interfaces.etas import EtasBus
from can import Message
from can.io.blf import BLFWriter  
import threading

# 全局变量，用于控制循环是否继续运行
running = True
paused = False

def can_listener():
    global running, paused
    bitrate = 500000
    blf_writer = BLFWriter('test7.blf', append=False)
    
    # 配置CAN总线
    try:
        bus = EtasBus(channel='ETAS://USB/ES582.1:4224472/CAN:1', bitrate=bitrate, receive_own_messages=False, fd=True)
        print(bus)

        recvNum = 0
        while running:
            if not paused:
                ret = bus.recv(timeout=0.1)  # 设置timeout防止阻塞
                if ret is not None:  # 确保接收到的不是None
                    print(ret)
                    print('=======================')
                    # 按照指定格式封装消息，需要按照特定格式封装，才能成功录制报文。
                    obj_msg_tmp = Message(
                        timestamp=ret.timestamp,
                        arbitration_id=ret.arbitration_id,
                        is_extended_id=ret.is_extended_id,
                        is_remote_frame=ret.is_remote_frame,
                        is_error_frame=ret.is_error_frame,
                        channel=ret.channel,
                        data=ret.data,
                        is_fd=ret.is_fd,
                        is_rx=ret.is_rx,
                        bitrate_switch=ret.bitrate_switch,
                        error_state_indicator=ret.error_state_indicator
                    )
                    blf_writer.on_message_received(obj_msg_tmp)  # 使用正确的写入方法
                    print(ret)
                    recvNum += 1
                    print("num is {}".format(recvNum))
            else:
                time.sleep(0.1)  # 当暂停时，减少CPU使用率

        blf_writer.stop()  # 确保在退出前停止BLFWriter
        bus.shutdown()

    except Exception as e:
        print(f"Error: {e}")
        blf_writer.stop()  # 发生异常时也确保停止BLFWriter
        bus.shutdown()  # 清理资源

# 需要正常停止，才能可以成功保存文件。
def key_listener():
    global running, paused
    while running:
        key = input("Press 'p' to pause/resume or 'q' to quit: ")
        if key == 'p':
            paused = not paused
            print(f"{'Paused' if paused else 'Resumed'}")
        elif key == 'q':
            running = False
            print("Quitting...")

if __name__ == "__main__":
    # 创建线程
    thread_can_listener = threading.Thread(target=can_listener)
    thread_key_listener = threading.Thread(target=key_listener)

    # 启动线程
    thread_can_listener.start()
    thread_key_listener.start()

    # 等待两个线程完成
    thread_can_listener.join()
    thread_key_listener.join()
