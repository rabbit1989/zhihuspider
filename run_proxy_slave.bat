set PYTHONPATH=%PYTHONPATH%;../;./crawler/;./logic/;./proxy;
start python crawler\crawl_slave.py proxy\slave_config.ini log\proxy_slave1
start python crawler\crawl_slave.py proxy\slave_config.ini log\proxy_slave2
rem start python crawler\crawl_slave.py proxy\slave_config.ini log\proxy_slave3