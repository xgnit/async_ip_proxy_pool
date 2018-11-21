# proxy_pool

after importing the file, use the following to get the proxy pool.

### res = Proxy().get_proxy()

the variable res will be a list of strings, the strings will have the format like 'https://111.222.333.444:1234'.
This process fetches some proxies from internet and local file and then test if they are still available.



Or if you do not want to test the proxies but just use the proxies in the local file. Set the update parameter as False
as following:

### res = Proxy(update=False).get_proxy()


notes:
install progressbar2 but not progressbar



#中文版
使用如下方式获取代理ip池

### res = Proxy().get_proxy()

这个res是一个string的list。string的形式如：'https://111.222.333.444:1234'。
这个过程会从网络上下载一些代理ip然后和本地保存的代理ip一起测试，看它们是否还都是可用的。



或者如果你只想用本地保存的代理ip。将Proxy构造函数里的update变量设为False如下：

### res = Proxy(update=False).get_proxy()


注意安装的是progressbar2而不是progressbar
