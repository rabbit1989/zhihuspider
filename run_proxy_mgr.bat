set PYTHONPATH=%PYTHONPATH%;../;./crawler/;./logic/;./proxy;
python proxy\proxy_master.py
rem start python crawler\crawl_slave.py proxy\slave_config.ini log\proxy_slave1
rem start python crawler\crawl_slave.py proxy\slave_config.ini log\proxy_slave2
rem start python crawler\crawl_slave.py proxy\slave_config.ini log\proxy_slave3
rem start python crawler\crawl_slave.py proxy\slave_config.ini log\proxy_slave4
rem start python crawler\crawl_slave.py proxy\slave_config.ini log\proxy_slave5


