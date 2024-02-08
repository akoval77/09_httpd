# 09 Automatizaton homework - httpd

The given code is a Python script that creates a simple HTTP server. It listens on a specified port, accepts incoming connections, and serves files from a specified document root directory. Server supports scalability by using pre-fork worker model. 

## Usage
```
httpd.py [-h] [-w W] [-p P] [-r R]

options:
  -h, --help  show this help message and exit
  -w W        number of workers (default 4)
  -p P        port (default 80)
  -r R        Path to document directory
```
Example:
```bash
python httpd.py -w 4 -r ./http-test-suite 
```

## Load testing results

Tests ran on 4-core virtual machine under Ubuntu 20.04

For load testing 2 urls were used
- http://localhost/httptest/   - returns HTTP 404
- http://localhost/httptest/dir2/ - returns HTTP 200 and content of /httptest/dir2/index.html


1. Single worker (no parallel processing)

```bash
python httpd.py -w 1 -r ./http-test-suite 
```
ab tool output for http://localhost/httptest/
```
$ ab -c 100 -n 50000 http://localhost/httptest/

Document Path:          /httptest/
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   2.199 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      5450000 bytes
HTML transferred:       0 bytes
Requests per second:    22735.22 [#/sec] (mean)
Time per request:       4.398 [ms] (mean)
Time per request:       0.044 [ms] (mean, across all concurrent requests)
Transfer rate:          2420.06 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.3      0       4
Processing:     1    4   0.7      4       9
Waiting:        0    4   0.7      4       9
Total:          2    4   0.7      4       9

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      4
  75%      5
  80%      5
  90%      5
  95%      6
  98%      6
  99%      7
 100%      9 (longest request)

```

ab tool output for http://localhost/httptest/dir2/ 
```
$ ab -c 100 -n 50000 http://localhost/httptest/dir2/

Document Path:          /httptest/dir2/
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   6.620 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      9050000 bytes
HTML transferred:       1700000 bytes
Requests per second:    7553.02 [#/sec] (mean)
Time per request:       13.240 [ms] (mean)
Time per request:       0.132 [ms] (mean, across all concurrent requests)
Transfer rate:          1335.06 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       5
Processing:     1   13   1.2     13      21
Waiting:        1   13   1.2     13      21
Total:          3   13   1.1     13      21

Percentage of the requests served within a certain time (ms)
  50%     13
  66%     14
  75%     14
  80%     14
  90%     14
  95%     15
  98%     16
  99%     16
 100%     21 (longest request)

```
2. 4 workers 

```bash
python httpd.py -w 4 -r ./http-test-suite 
```

ab tool output for http://localhost/httptest/

```
ab -c 100 -n 50000 http://localhost/httptest/

Document Path:          /httptest/
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   2.966 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      5450000 bytes
HTML transferred:       0 bytes
Requests per second:    16859.25 [#/sec] (mean)
Time per request:       5.931 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
Transfer rate:          1794.59 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    3   0.7      3       7
Processing:     1    3   0.9      3      15
Waiting:        0    2   0.8      2      14
Total:          3    6   1.1      6      18

Percentage of the requests served within a certain time (ms)
  50%      6
  66%      6
  75%      7
  80%      7
  90%      7
  95%      8
  98%      9
  99%      9
 100%     18 (longest request)

```

ab tool output for http://localhost/httptest/dir2/ 

```
ab -c 100 -n 50000 http://localhost/httptest/dir2/

Document Path:          /httptest/dir2/
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   2.782 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      9050000 bytes
HTML transferred:       1700000 bytes
Requests per second:    17971.09 [#/sec] (mean)
Time per request:       5.564 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Transfer rate:          3176.53 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2   1.3      2      13
Processing:     0    3   1.4      3      34
Waiting:        0    3   1.3      2      33
Total:          3    6   2.3      5      37

Percentage of the requests served within a certain time (ms)
  50%      5
  66%      5
  75%      6
  80%      6
  
  90%      7
  95%     12
  98%     14
  99%     15
 100%     37 (longest request)

```

3. 8 workers


ab tool output for http://localhost/httptest/ 

```
$ ab -c 100 -n 50000 http://localhost/httptest/

Server Software:        Dummy
Server Hostname:        localhost
Server Port:            80

Document Path:          /httptest/
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   3.829 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      5450000 bytes
HTML transferred:       0 bytes
Requests per second:    13059.23 [#/sec] (mean)
Time per request:       7.657 [ms] (mean)
Time per request:       0.077 [ms] (mean, across all concurrent requests)
Transfer rate:          1390.09 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    4   0.9      4      11
Processing:     0    4   1.1      4      14
Waiting:        0    3   1.0      3      13
Total:          3    8   1.4      8      20

Percentage of the requests served within a certain time (ms)
  50%      8
  66%      8
  75%      8
  80%      9
  90%      9
  95%     10
  98%     11
  99%     11
 100%     20 (longest request)
```

ab tool output for http://localhost/httptest/dir2/ 
```
$ ab -c 100 -n 50000 http://localhost/httptest/dir2/

Document Path:          /httptest/dir2/
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   3.708 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      9050000 bytes
HTML transferred:       1700000 bytes
Requests per second:    13483.45 [#/sec] (mean)
Time per request:       7.416 [ms] (mean)
Time per request:       0.074 [ms] (mean, across all concurrent requests)
Transfer rate:          2383.31 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    3   1.5      3      11
Processing:     1    4   1.5      4      28
Waiting:        0    3   1.3      3      28
Total:          3    7   2.5      7      29

Percentage of the requests served within a certain time (ms)
  50%      7
  66%      8
  75%     10
  80%     10
  90%     11
  95%     11
  98%     12
  99%     14
 100%     29 (longest request)

```