## sharp

### 解决什么问题？

1.增量CVE数据的T级监控
2.EXP预警
3.全局自动化
4.威胁情报收集

### 产出及价值

做为外部威胁情报，为企业及攻防双方提供有价值的威胁情报及CVE数据和建议。

### 痛点

适配新的网站总是要写冗余的代码。目前采用配置的形式
只要有新的需求就可以通过定义的语法进行添加。

### 结论
待续

### 杂乱
目前该爬虫为增量爬虫

全量爬取作为基础数据，需要编写额外的代码，一次执行即可。


### browserless

browserless 解决问题 https://docs.browserless.io/docs/docker-quickstart.html

```
docker run -d -p 3000:3000 \
    -e DEBUG=browserless* \
    -e PREBOOT_CHROME=true -e MAX_CONCURRENT_SESSIONS=10 -e KEEP_ALIVE=true
    --name browserless browserless/chrome:latest
```

当负载很高的情况下，Chrome 启动可能会花上好几秒钟。对大多数情况来说，我们还是希望避免这个启动时间。所以，最好的办法就是预先启动好 Chrome，然后让他在后台等着我们调用。

如果使用 browserless/chrome 这个镜像的话，直接指定 PREBOOT_CHROME=true 就好了。下面的命令会直接启动 10 个浏览器，如果你指定 KEEP_ALIVE，那么在你断开链接(pp.disconnect)的时候也不会关闭浏览器，而只是把相关页面关闭掉。

browserless 的镜像一个核心功能是无缝限制并行和使用队列。也就是说消费程序可以直接使用 puppeteer.connect 而不需要自己实现一个队列。这避免了大量的问题，大部分是太多的 Chrome 实例杀掉了你的应用的可用资源。

上面限制了并发连接数到10，还可以使用MAX_QUEUE_LENGTH来配置队列的长度。总体来说，每1GB内存可以并行运行10个请求。CPU 有时候会占用过多，但是总的来说瓶颈还是在内存上。

browserless 家的镜像还有一个功能就是提供了屏蔽广告的功能。屏蔽广告可以是你的流量降低，同时提升加载速度。

只需要在连接的时候加上 blockAds 参数就可以了。
