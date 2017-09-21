set PYTHONPATH=%PYTHONPATH%;../;./crawler/;./logic/;
start python crawler\crawl_slave.py log\slave1
ping localhost -n 1