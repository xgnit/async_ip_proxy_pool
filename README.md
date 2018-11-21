# proxy_pool

after importing the file, use the following to get the proxy pool.

res = Proxy().get_proxy()

the variable res will be a list of strings, the strings will have the format like 'https://111.222.333.444:1234'
This process fetches some proxies from internet and local file and then test if they are still available.



Or if you do not want to test the proxies but just use the proxies in the local file. Set the update parameter as False
as following:

res = Proxy(update=False).get_proxy()
