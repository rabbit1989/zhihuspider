set PYTHONPATH=%PYTHONPATH%;../;./crawler/;./logic/;
start python crawler\crawl_slave.py crawler\config.ini log\slave31
ping localhost -n 5
start python crawler\crawl_slave.py crawler\config.ini log\slave32
ping localhost -n 5
start python crawler\crawl_slave.py crawler\config.ini log\slave33
ping localhost -n 5
start python crawler\crawl_slave.py crawler\config.ini log\slave34
ping localhost -n 5
start python crawler\crawl_slave.py crawler\config.ini log\slave35
ping localhost -n 5
start python crawler\crawl_slave.py crawler\config.ini log\slave36
ping localhost -n 5
start python crawler\crawl_slave.py crawler\config.ini log\slave37
ping localhost -n 5
start python crawler\crawl_slave.py crawler\config.ini log\slave38

