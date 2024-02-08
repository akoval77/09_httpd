from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import multiprocessing
import argparse
from os import path, getpid, stat
from urllib import parse
import time
import signal
import sys
from mimetypes import guess_type
import traceback
from datetime import datetime, timezone

MAXLINE = 65536
CRLF = b'\r\n'

HTTP_OK = (200, 'OK')
HTTP_BAD_REQUEST = (400, 'Bad Request')
HTTP_NOT_FOUND = (404, 'Not Found')
HTTP_METHOD_NOT_ALLOWED = (405, 'Method Not Allowed')
HTTP_REQUEST_URI_TOO_LONG = (414, 'Request-URI Too Long')
HTTP_INTERNAL_SERVER_ERROR = (500, 'Internal Server Error')


HTTP_VERSION = 'HTTP/1.1'


class HTTPBadRequest(Exception):
    pass


def send_error(conn, code, message, detail=None):
    response = f"{HTTP_VERSION} {code} {message}\r\n"
    response += "Server: Dummy OTUS server\r\n"
    dt = httpdate(datetime.now(timezone.utc))
    response += f"Date: {dt}\r\n"
    response += "Connection: close\r\n\r\n"
    if detail:
        response += detail

    print(response)
    conn.sendall(response.encode('utf-8'))

    conn.close()


def get_file_size(file_path):
    file_stats = stat(file_path)
    return file_stats.st_size


# https://stackoverflow.com/questions/225086/rfc-1123-date-representation-in-python
def httpdate(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)


def send_file_content(conn, file_path):
    with open(file_path, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(1024)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in
            # busy networks
            conn.sendall(bytes_read)


def send_response(conn, file_path, send_body):
    response = "HTTP/1.1 200 OK\r\n"
    response += "Server: Dummy OTUS server\r\n"
    dt = httpdate(datetime.utcnow())
    response += f"Date: {dt}\r\n"
    if file_path.endswith(".js"):
        content_type = "text/javascript"
    else:
        content_type, _ = guess_type(file_path)
    content_length = get_file_size(file_path)
    response += f"Content-Type: {content_type}\r\n"
    response += f"Content-Length: {content_length}\r\n"
    response += "Connection: close\r\n\r\n"

    print(response)
    # отправляем ответ клиенту
    conn.sendall(response.encode('utf-8'))
    # print(f"Sent {sent} bytes")

    if send_body:
        send_file_content(conn, file_path)

    # time.sleep(0.5)
    # закрываем соединение
    conn.close()


def handle_request(conn, addr, doc_root):
    try:
        # получаем данные от клиента
        data = conn.recv(MAXLINE+1)

        # выводим информацию о запросе
        # print(f"pid: {getpid()},  Received {data} from {addr}")

        raw_request = data.split(CRLF, 1)[0]
        if len(raw_request) > MAXLINE:
            send_error(conn, *HTTP_REQUEST_URI_TOO_LONG)
            return

        try:
            (method, url, version) = str(raw_request, 'iso-8859-1').split()
            print(f"{method} {url}")
        except ValueError:
            send_error(conn, *HTTP_BAD_REQUEST)
            return

        if method not in ('GET', 'HEAD'):
            send_error(conn, *HTTP_METHOD_NOT_ALLOWED)
            return

        url = parse.unquote(url.split("?")[0])

        if "/../" in url:
            send_error(conn, *HTTP_NOT_FOUND)
            return

        if url.endswith('/'):
            url += 'index.html'

        file_path = path.normpath(doc_root + "/" + url)

        if not path.isfile(file_path):
            send_error(conn, *HTTP_NOT_FOUND)
            return

        send_response(conn, file_path, method == 'GET')
    except Exception as e:
        print(traceback.format_exc())
        send_error(conn, *HTTP_INTERNAL_SERVER_ERROR, detail=f"{e}")


def process_connections(s, doc_root):
    while True:
        # Принимаем соединение
        conn, addr = s.accept()
        # Печатаем адрес клиента
        print(f"Accepted connection from {addr}")
        handle_request(conn, addr, doc_root)
        # time.sleep(0.1)


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
    parser.add_argument('-r', type=str, default=r'./http-test-suite', help='Path to document directory')

    # Разбираем аргументы
    args = parser.parse_args()

    # get document root
    root_path = path.abspath(args.r)
    if not path.isdir(root_path):
        print(f"Invalid document root {root_path}")
        exit(1)

    print(f"Document root: {root_path}")

    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Привязываем сокет к адресу и порту
    s.bind(("localhost", 80))
    # Начинаем прослушивать входящие соединения
    s.listen()

    signal.signal(signal.SIGINT, signal_handler)

    # Создаем список процессов-обработчиков
    workers = []
    # Запускаем процессы-обработчики
    for i in range(args.w):
        # Создаем процесс
        p = multiprocessing.Process(target=process_connections, args=(s, root_path,))
        # Добавляем процесс в список
        workers.append(p)
        # Запускаем процесс
        p.start()

    while True:
        time.sleep(0.5)


if __name__ == '__main__':
    main()

