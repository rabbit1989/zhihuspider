set PYTHONPATH=%PYTHONPATH%;../;./crawler/;./logic/;
start python crawler\crawl_slave.py crawler\config.ini log\slave1
ping localhost -n 1
start python crawler\crawl_slave.py crawler\config.ini log\slave21
ping localhost -n 1
start python crawler\crawl_slave.py crawler\config.ini log\slave22
ping localhost -n 1
start python crawler\crawl_slave.py  crawler\config.ini log\slave4
ping localhost -n 1
start python crawler\crawl_slave.py crawler\config.ini  log\slave5
ping localhost -n 1
start python crawler\crawl_slave.py  crawler\config.ini log\slave6
ping localhost -n 1
start python crawler\crawl_slave.py crawler\config.ini  log\slave7
ping localhost -n 1
start python crawler\crawl_slave.py  crawler\config.ini log\slave8
ping localhost -n 1
start python crawler\crawl_slave.py crawler\config.ini  log\slave9
ping localhost -n 1
start python crawler\crawl_slave.py  crawler\config.ini log\slave10
ping localhost -n 1
rem start python crawler\crawl_slave.py crawler\config.ini  log\slave1
rem ping localhost -n 1
rem start python crawler\crawl_slave.py crawler\config.ini  log\slave12
rem ping localhost -n 1
rem start python crawler\crawl_slave.py  crawler\config.ini log\slave13
rem ping localhost -n 1
rem start python crawler\crawl_slave.py  crawler\config.ini log\slave14
rem ping localhost -n 1
rem start python crawler\crawl_slave.py crawler\config.ini  log\slave15
rem ping localhost -n 1
rem start python crawler\crawl_slave.py  crawler\config.ini log\slave16
rem ping localhost -n 1
rem start python crawler\crawl_slave.py crawler\config.ini  log\slave17
rem ping localhost -n 1
rem start python crawler\crawl_slave.py  crawler\config.ini log\slave18
rem ping localhost -n 1
rem start python crawler\crawl_slave.py  crawler\config.ini log\slave19
rem ping localhost -n 1
rem start python crawler\crawl_slave.py crawler\config.ini  log\slave20



