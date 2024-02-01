import socket
import multiprocessing
import argparse
import os
import time
import signal
import sys


def handle_request(conn, addr):
    # получаем данные от клиента
    data = conn.recv(1024)
    # выводим информацию о запросе
    print(f"pid: {os.getpid()},  Received {data} from {addr}")
    # формируем ответ
    response = b"HTTP/1.1 200 OK\r\n"
    response += b"Content-Type: text/plain\r\n"
    response += b"Connection: close\r\n\r\n"
    response += b"Hello, world!"
    # отправляем ответ клиенту
    sent = conn.send(response)
    print(f"Sent {sent} bytes")
    time.sleep(0.5)
    # закрываем соединение
    conn.close()


def process_connections(s):
    while True:
        # Принимаем соединение
        conn, addr = s.accept()
        # Печатаем адрес клиента
        print(f"Accepted connection from {addr}")
        handle_request(conn, addr)
        time.sleep(0.1)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    for process in multiprocessing.active_children():
        print(f"Shutting down process {process}")
        # logging.info("Shutting down process %r", process)
        process.terminate()
        process.join()
    sys.exit(0)


def main():
    # Создаем парсер аргументов
    parser = argparse.ArgumentParser()
    # Добавляем аргумент -w для указания количества обработчиков
    parser.add_argument("-w", type=int, default=4, help="number of workers")
    # Разбираем аргументы
    args = parser.parse_args()

    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Привязываем сокет к адресу и порту
    s.bind(("localhost", 8080))
    # Начинаем прослушивать входящие соединения
    s.listen()

    signal.signal(signal.SIGINT, signal_handler)

    # Создаем список процессов-обработчиков
    workers = []
    # Запускаем процессы-обработчики
    for i in range(args.w):
        # Создаем процесс
        p = multiprocessing.Process(target=process_connections, args=(s,))
        # Добавляем процесс в список
        workers.append(p)
        # Запускаем процесс
        p.start()

    while True:
        time.sleep(0.5)


if __name__ == '__main__':
    main()
