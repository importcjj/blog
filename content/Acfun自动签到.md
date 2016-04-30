Title: 简单的Acfun自动签到
Category: sundry
Tags: shell, contab, curl
Date: 2016-04-30 23:38:20
Author: importcjj

### 1.概述

Acfun有一个签到机制，每天签到可以领取经验和香蕉。之前在玩supervisor，celerybeat和rabbitmq的时候搞了一个自动签到的定时任务，但是由于服务器的原因，每天都会出问题。而且前段时间，那台服务器也到期了，所以现在有必要再搞一个简单的自动签到任务了。：）


### 2. 签到

为了简便，这里就不使用Python了。直接curl搞定吧！上代码：

``` sh
curl --cookie-jar cookies -d "username=name&password=passwd" http://www.acfun.tv/login.aspx && echo
curl --cookie cookies -d "channel=0&date=`date +%s`000" http://www.acfun.tv/webapi/record/actions/signin && echo

```

简单说明一下， A站签到要求先登录，所以我们脚本的第一步使用自己的账户密码登录并且把cookie存放在本地文件中。然后第二步直接读取cookie完成签到。其实问题就在于签到请求需要带有date参数，它其实是JavaScript的时间戳。将上述代码保存为 **checkin.sh** 就基本上完成了代码部分。是不是很简单？


### 3. 自动化

使用linux的crontab来完成定时任务。在*unix下为当前用户添加一个crontab任务吧。

1. 开始编辑 `crontab -e`
2. 添加一行 `0 1 * * * sh /path/to/checkin.sh > /path/to/checkin.log`
3. 保存退出

这样就会在每天一点的时候执行一次签到。：）



## 4. 结束

感觉好水啊！



