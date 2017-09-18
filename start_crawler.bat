set PYTHONPATH=%PYTHONPATH%;../;./crawler/;./logic/;
start python crawler\crawl_master.py
ping localhost -n 1
start python crawler\proxy_mgr.py 1
ping localhost -n 1
start python crawler\proxy_mgr.py 2


