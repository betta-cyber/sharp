# 爬虫引擎语法

## 导读

爬虫引擎从YAML文件当中读取结构化数据，并根据相应的语法进行爬虫解析

### Q&A: 为什么选择YAML，而不是JSON，XML或者其他的结构化文本格式? 

YAML是JSON的超集且：

- YAML的值无需使用双引号包裹，所以特殊字符无需转义
- YAML的内容更加可读
- YAML中可以使用注释

其实TOML挺好的，这种格式易于阅读，但是我个人觉得YAML已经可以胜任这个工作。

至于XML，现在没人手写XML了吧

## 结构

通常来讲，语法是通用的。但是还是做一个分类，因为在爬虫爬取的过程中，我们想要爬取到信息大致分为以下两种情况，一种是根据页面获取到列表，从列表中提取到信息。然后入库，一种是通过先获取到列表的部分内容，然后结合获取到的具体页面的URL详情内容组装起来，然后再入库。

### 获取列表语法

```
-
  url: "http://www.djbh.net/webdev/web/HomeWebAction.do?p=getlistHomeXxgg"
  event_type: "新闻动态"
  source: "等保门户网"
  pattern:
    type: "table"
    list_class: "#idData > tbody"
  basetime:
    pattern: "\\d{4}-\\d{2}-\\d{2}"
-
  url: "http://www.djbh.net/webdev/web/HomeWebAction.do?p=getlistHomeXxgg"
  event_type: "新闻动态"
  source: "等保门户网"
  pattern:
    type: "table"
    list_class: "#idData > tbody > tr"
  basetime:
    pattern: "\\d{4}-\\d{2}-\\d{2}"
```
先看例子：
整体的文件名命名为`rule/event/list/djbh.yml` 是指我们这是规则集当中的获取event（也就是安全事件）的列表内容的对应的网站是djbh（也就是等保网）的信息。

那么上来我们的YAML格式为一个大数组，那是因为我们针对djbh这个网站，可能有不同的分类需要爬取。那就对对应不同的url或者不同的规则。

然后开始定义相关的内容

- url 是需要爬取的url的地址
- event_type 是自己定义的事件的类型这里是和这个安全事件相关的。
- source 是来源
- pattern 是关键的字段，我们的代码就是根据pattern来做匹配的
   - type 规则匹配的类型 （table ）
   - list_class 是可选字段  有的话，会根据这个来做匹配

### 获取详情语法

```
title:
  type: selector
  struct: string
  pattern: "#WenziB > span"
start:
  type: func
  struct: list
  pattern: "find_time"
  dom: "#zhongwenzi"
abstract:
  type: selector
  struct: string
  length: 200
  pattern: "#zhongwenzi > blockquote"
raw_url:
  type: system
  struct: string
  pattern: $url
source:
  type: static
  struct: string
  pattern: "网络安全等级保护网"
event_type:
  type: system
  struct: string
  pattern: $event_type
weight:
  type: func
  struct: string
  pattern: "get_weight"
  dom: "#zhongwenzi"
```

这里是`rule/event/detail/djbh.yml`的规则文件

**获取详情的规则是一定会用pyppeteer来打开页面的。所有需要什么内容都可以在里面规定好。**

这里的字段都是由自己的模块定义的，比如我是event模块，那我最后通过pipeline返回的时候的字典里面就是包含这些定义的字段。

比如我这里最后就会返回一个字典包含title，start，abstract，raw_url，source，event_type，weight这些字段，只是把这些字段的值用后面的规则取代掉了。

```
type: selector  必填
struct: string   必填
pattern: "#WenziB > span"   必填
```

常见的写法是 type规定我的这个获取值，是用什么方法，比如这里用的是 **selector** ，表示用的是选择器来获取，那 **pattern** 里面跟的就是具体的选择器用到的值的内容。然后最后会通过struct来规范化，我要的这个值是什么类型的，进行转换。

然后可选的字段我列在下面

- length: 200  表示长度为200， 使用python当中 start:end 的切片语法可以对结果进行切片。

然后还有一些辅助方法：

type 为func的时候会有一些内置的方法，或者通过自己实现的插件的方法进行拓展

比如 "get_weight"是我写的插件的方法，目的是通过结巴分词，对文本进行出来，返回其文本的权重值
再比如 "find_time"是我写的找出自然语言中存在的时间节点的方法，故最后的strcut为list。至于他们所用到dom字段，是制定他在那个dom的范围内进行这些方法的执行。此处还可以有很多优化。

再比如插件的代码，目前我都放在module目录下面，后续需要进一步规范化插件的编写。

type为 **static** 的时候，就是静态资源。直接返回

type为 **sytem** 的时候，就是系统的内置变量，直接返回系统变量




### 语法（新版）

#### JSON结构示例
``` 
-
  url: $requests
  data-format: "json"
  data:
    url: "http://wechat.doonsec.com/tags/?page=1&cat_id=3&_=1593596767797"
  source: "doonsec"
  pattern:
    type: "list"
    selector: "data"
  response:
    title:
      type: key
      struct: string
      pattern: "title"
    raw_url:
      type: key
      struct: string
      pattern: 'url'
    summary:
      type: key
      struct: string
      pattern: "digest"
    source:
      type: key
      struct: string
      pattern: "account_name"
    publish_time:
      type: key
      struct: string
      pattern: "publish_time" 
``` 

#### JSON类型的数据接口的示例

首先url写成$requests，表示此处要使用requests。因为爬虫部分主要获取的方式有通过requests库来采集网页和用pyppeteer来采集网页。

这里其实有点不对

data-format定义的是json。表示需要在后续的分析当中使用json。

**data-format** 常见的是**html** 还有 **json**，**rss**后面可能会有**xml**等形式，数据格式的定义不同后续进行的处理也会不同。

**data** 里面data存储的是url需要用到的相关数据。

**pattern** 字段很关键，它表示我们要找的一个列表在我们内容当中是哪个位置，这里用的是selector。

**response** 定义我们需要返回的数据结构

然后在response中我们会用到一些方法，同上面提到的类似

数据必须包含 **type** **struct** **pattern** 字段，其他字段可选。

```
publish_time:          
	type: "key"            
	struct: "string" 
	pattern: "date"
```

如type为key的时候，就是把要处理的数据看作一个字典，我们根据key去取字典里面的数据就行了。

然后又如有些时候我们会需要一些需要拼装的组合，如

```
raw_url:
  type: hybrid-json
  struct: string
  pattern: "https://www.anquanke.com/post/id/{id}"
```
这里的raw_url字段想获取，那需要借助hybrid-json的方法，我们把我们要用到字段比如id用**大括号**符号封起来，这样就表示替代，代码会自动获取到id的值并关联起来。

### html类型接口示例

``` 
-
  url: $requests
  data-format: "html"
  data:
    url: "https://www.cnvd.org.cn/webinfo/list?type=1"
  source: "cnvd"
  pattern:
    type: "list"
    selector: "body > div.mw.Main.clearfix > div.blkContainer > div.blkContainerPblk > table > tbody > tr"
  response:
    title:
      type: tag
      struct: string
      pattern: "a"
    raw_url:
      type: hybrid
      struct: string
      pattern: 'https://www.cnvd.org.cn{title.href}'
    summary:
      type: func
      struct: string
      pattern: "get_text"
    source:
      type: static
      struct: string
      pattern: "cnvd"
    publish_time:
      type: func
      struct: string
      pattern: "filter_time" 
``` 

不需要太多的爬虫检测，故采用$requests，和上面一样，我这里通过选择器获取需要的列表。然后根据response来进行获取想要的内容。

#### 常见用法

- **tag** 在pattern中指定什么tag，这个一般可以满足需求，会返回找个找到的dom的text
- **hybrid** 混合用法，`https://www.cnvd.org.cn{title.href}` 这样的用法表示是获取title那个dom的href字段并进行替换
- **func** 内置方法
	- **get_text** 获取text
	- **filter_time** 从文本中获取筛选出时间戳
- **find_by_class** 从pattern当中写的规则获取他的文本  _"a|topic-title"_  前为tag名，后为class名。
- **static** 静态资源
- **selector** css选择器
- **system** 系统变量





























