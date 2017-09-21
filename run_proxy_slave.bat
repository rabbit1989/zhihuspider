set PYTHONPATH=%PYTHONPATH%;../;./crawler/;./logic/;./proxy;
start python proxy\proxy_slave.py log\proxy_slave1
start python proxy\proxy_slave.py log\proxy_slave2
start python proxy\proxy_slave.py log\proxy_slave3
start python proxy\proxy_slave.py log\proxy_slave4
start python proxy\proxy_slave.py log\proxy_slave5
