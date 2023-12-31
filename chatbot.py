import threading
import json
import requests
from utils.BotServer import BotServer
from models.IntentModel import IntentModel
from models.QuizModel import QuizModel
from models.GenerateModel import GenerateModel


# tensorflow gpu 메모리 할당
# tf는 시작시 메모리를 최대로 할당하기 때문에, 0번 GPU를 2GB 메모리만 사용하도록 설정
'''
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_visible_devices(gpus[0], 'GPU')
        tf.config.experimental.set_virtual_device_configuration(gpus[0],
                                                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)])
    except RuntimeError as e:
        print(e)
'''

def to_client(conn, addr):
    try:
        # 데이터 수신
        read = conn.recv(2048) # 수신 데이터가 있을 때까지 블로킹
        print('======================')
        print('Connection from: %s' % str(addr))

        if read is None or not read:
            # 클라이언트 연결이 끊어지거나 오류가 있는 경우
            print('클라이언트 연결 끊어짐')
            exit(0)  # 스레드 강제 종료

        # json 데이터로 변환
        recv_json_data = json.loads(read.decode())
        print("데이터 수신 : ", recv_json_data)
        query = recv_json_data['Query']

        # 답변 생성
        if recv_json_data['BotType'] == 'NORMAL':
            lab = IntentModel.generate_answer(query)
            #answer = GenerateModel.generate_text(query, lab)
            answer = '하하'
            send_json_data_str = {
                "Answer": answer,
                "label": lab
            }
        elif recv_json_data['BotType'] == 'QUIZ':
            answer, lab = QuizModel.get_quiz(query)
            send_json_data_str = {
                "Answer": answer,
                "label": lab
            }

        message = json.dumps(send_json_data_str) # json객체 문자열로 반환
        conn.send(message.encode()) # 응답 전송

        # CORS 헤더 설정
        response_headers = {
            'Access-Control-Allow-Origin': 'https://3.36.6.123',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        conn.send(json.dumps(response_headers).encode())

    except Exception as ex:
        print(ex)



if __name__ == '__main__':
    # 봇 서버 동작
    port = 5050
    listen = 1000
    bot = BotServer(port, listen)
    bot.create_sock()
    print("bot start..")

    while True:
        conn, addr = bot.ready_for_client()
        client = threading.Thread(target=to_client, args=(
            conn,   # 클라이언트 연결 소켓
            addr,   # 클라이언트 연결 주소 정보
        ))
        client.start()
