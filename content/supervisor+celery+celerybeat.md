Title: supervisor+celery+celerybeat的简单使用
Category: Python
Tags: supervisor, celery, Python
Date: 2016-03-27 03:37:03
Authors: importcjj



## 1. 提前准备

略去相关工具的安装过程，其实都挺简单的!

celery作为异步任务队列, 需要一个中间人来协助celery存放和消耗任务信息。我们选择rabbitmq来做消息代理人。使用celery之前, 需要使用创建一个rabbitmq的管理员账号和一个能让该账号访问的vhost.

**[Rabbitmq的安装配置以及网页管理插件]()**

假设准备的rabbitmq的信息如下:

``` python
SETTINGS = {
    'user': 'www-data',
    'password': 'www-data',
    'host': '127.0.0.1',
    'port': '5672',
    'vhost': 't_celery'
}
```

### 示例项目结构

``` 
test.celery/
	|- env/
	|- src/
		|- __init__.py
		|- app.py
		|- task.py
```

## 2. celery实例及任务

### 2.1 生成实例

``` python
# -*- coding: utf-8 -*-

# filename: app.py

from celery import Celery

CELERY_CONFIG = {
    'CELERY_TIMEZONE': 'Asia/Shanghai',
    'CELERY_ENABLE_UTC': True,
    # content
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERY_RESULT_SERIALIZER': 'json',
    'CELERY_ACCEPT_CONTENT': ['json'],
    'CELERYD_MAX_TASKS_PER_CHILD': 1,
}

# 第一个参数是实例的名称,  也可以使用模块的名字.
# broker参数是消息代理人url.
# 还有一个backend参数，当我们需要拿到异步任务的返回时需要用到.
# 这里就直接略过了.
app = Celery(
    'test_celery',
    broker='amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
        **SETTINGS)
)
app.conf.update(**CELERY_CONFIG)
```

### 2.2 定义Task

``` python
# -*- coding: utf-8 -*-

# filename: task.py

from src.app import app

@app.task(queue='test_celey_queue')
def add(x, y, c=0):
    return x + y + c
```

注意, 我们给app.task这个装饰器传了queue这个参数, 这样当异步执行的时候,这个task会被丢到名称为test\_celery\_queue的队列中, 然后被为这个队列工作的worker拿到并执行。当然， 我们也可以在CELERY_CONFIG中配置:

``` python
CELERY_ROUTES = {
     'src.task.add': 'test_celery_queue',
}
```

如果我们不指定queue的话，celery会默认自己指定一个队列。task的队列一定要对应的worke， 否者就会只生产不消费， 这些task就永远不会被执行了。

### 2.3 启动worker

我们需要在项目路径下，也就是test.celery文件下运行python解释器， 否者python解释器无法找到 **src** 这个包。 或者直接将项目路径添加到PYTHONPATH变量，就像这样```export PYTHONPATH=/data/test.celery```

然后再启动worker：

``` sh
celery worker -A src.task --loglevel=info -Q test_celery_queue -f /data/test.celery/celery.log
```

##### 参数解析

1. - A src.task 指定celery实例, celery会到src.task中找app实例
2. worker 告知celery要启动worker.
3. --loglevel=info 日志的级别是info.
4. -Q test\_celery_queue 为该worker指定一个消息队列, worker只取该队列中的任务。可以指定多个队列.
5. -f 日志文件输出位置
6. -P

更多可配置参数s通过 ```celery worker -h```  查看。

### 2.4 验证正确性

##### 在一个终端显示日志

``` 
tail -f /data/test.celery/celery.log
```

##### 另一个终端启动python的交互解释器

###### 注：如果没有设置PYTHONPATH， 那就要在我们的项目文件夹下启动

``` 
>>> from src.task import add
>>> add(4, 6)
10
>>> add.delay()
<AsyncResult: fe9b4b75-6ba8-44aa-adb2-92d63c8ba1c6>
>>> add.delay(4, 4)
<AsyncResult: e6dfcdbb-7a19-4fb2-aa5e-841b8f393874>
>>> add.apply_async(args=(3,5))
<AsyncResult: 34cf6a59-35db-40d3-a218-6703eb04336b>
```

如果一切正常的话，运行第二、三、四条命令的时候会看到有日志输出。而且第二条命令会有错误日志，提示缺少参数。

##### 用法说明

如果直接调用某一个task, 那么该task就跟普通的函数一样, 会同步运行并直接返回结果。想要异步执行, 就要使用 **delay** 或者 **apply_async** 。

* **delay:** 相对简单，怎么给**add**传参，就怎么传给它。比如:
  
  ```add.delay(4, 5, 9)``` 或者 ```add.delay(4 , 5, c=19)```等. 
  
* **apply_async:** 列举几个常用的参数:
  
``` 
  * args: 传给task的参数.
  * kwargs: 传给task的参数.
  * countdown： 延时执行的秒数.countdown=10表示10s后执行.
  * eta: datetime类型, 执行的日期.
  * queue: 指定任务消息要去的队列.
  * ...
```

## 3. celery beat

我们以定时发邮件为例子

### 3.1 添加发邮件的task

在task.py的基础上修改:

``` python
# -*- coding: utf-8 -*-

from src.app import app
from posts import Posts
import time

@app.task(queue='test_celery_queue')
def add(x, y, c=0):
    return x + y + c

@app.task
def sendmail():
    post = Posts('smtp.qq.com', 'emailname@qq.com', 'password', port=465)
    with post(ssl=True) as mail:
        mail.text(
            recipient ='receive@163.com,
            subject='send by celery beat',
            content=time.ctime()
        )
```

由于Python标准库发邮件有点繁琐，我这里使用了自己简单封装的[posts][1]来发送邮件。邮件的内容就是执行任务的时间。

### 3.2 配置定时任务的schedule

``` python
# -*- coding: utf-8 -*-

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'send-email-every-30-minutes': { 	# 定时任务的名字
        'task': 'src.task.sendmail',	 # 具体对应的Task
        'schedule':  timedelta(seconds=30),# 定时设置，这里表示30s执行一次
        # 'args': () ,       # 传给Task的参数
        'options': {     # 设置Task的一些属性, 参见apply_async的参数
            'queue':'test_celery_queue'
        }
    }
}
CELERY_CONFIG = {
    'CELERY_TIMEZONE': 'Asia/Shanghai',
    'CELERY_ENABLE_UTC': True,
    # content
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERY_RESULT_SERIALIZER': 'json',
    'CELERY_ACCEPT_CONTENT': ['json'],
    'CELERYD_MAX_TASKS_PER_CHILD': 1,
    'CELERYBEAT_SCHEDULE': CELERYBEAT_SCHEDULE     # 启动beat，传入相关参数.
}
SETTINGS = {
    'user': 'www-data',
    'password': 'www-data',
    'host': '127.0.0.1',
    'port': '5672',
    'vhost': 't_celery'
}

app = Celery(
    'test_celery',
    broker='amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
        **SETTINGS)
)
app.conf.update(**CELERY_CONFIG)
```

参数 **schedule** 说明, 通常使用两种方式来指定：

1. datetime.timedelta: 用这种方式来指定 秒 级别.
2. celery.shedules.crontab: 用这种方式指定 分钟 以上级别.

| Example                                  | 表示                    |
| ---------------------------------------- | --------------------- |
| timedelta(seconds=30)                    | 30秒执行一次               |
| crontab()                                | 每分钟执行一次               |
| crontab(minute=0, hour=0)                | 凌晨执行一次                |
| crontab(minute=0, hour='*/3')            | 从凌晨开始。每三个小时执行一次       |
| crontab(minute=0,hour='0,3,6,9,12,15,18,21') | 同上                    |
| crontab(minute='*/15')                   | 每15分钟执行一次             |
| crontab(day\_of\_week='sunday')          | 在周日，每分钟执行一次           |
| crontab(minute='*',hour='*', day\_of\_week='sun') | 同上                    |
| crontab(minute=0, hour='*/5')            | 每5小时执行一次,0,5,10,15,20 |
| crontab(0, 0, day\_of\_month='2')        | 每个月第二天执行一次            |
| crontab(0, 0, day\_of\_month='1-7,15-21') | 每月的1-7号和15-21号执行      |
| crontab(0, 0, day\_of\_month='11', month\_of\_year='5') | 5月份的11号执行一次           |
| crontab(0, 0,month\_of\_year='*/3')      | 每个季度的第一个月执行一次         |

更多用法详见 **[官方文档][2]**

### 3.3 启动celery beat

``` sh
celery beat -A src.app --loglevel=info --logfile=/data/test.celery/celery.beat.log
```

更多可配置参数通过 ```celery beat -h```  查看。

### 3.4 验证正确性

##### 一个页面显示celery beat 的输入日志

``` 
tail -f /data/test.celery/celery.beat.log
```

##### 一个终端页面显示 celery worker 输出日志

``` 
tail -f /data/test.celery/celery.log
```

如果分别能看到产生和消耗任务的日志输出。那就成功了。

## 4. supervisor

### 4.1 (supervisord)配置并启动supervisor

启动supervisor的命令是 **supervisord**。我们可以使用 **-c** 参数来指定其配置文件的位置。比如:

```supervisord -c supervisord.conf```

supervisor的配置文件 supervisord.conf:

``` ini
[unix_http_server]
file=/var/run/supervisor.sock                   ; (the path to the socket file)

[supervisord]
logfile=/data/log/supervisor/syslog         ; (main log file;default $CWD/supervisord.log)
loglevel=info                               ; (log level;default info; others: debug,warn,trace)
pidfile=/var/run/supervisord.pid                ; (supervisord pidfile;default supervisord.pid)
nodaemon=false                              ; (start in foreground if true;default false)
minfds=1024                               ; (min. avail startup file descriptors;default 1024)
minprocs=1024                             ; (min. avail process descriptors;default 200)
nocleanup=false
umask=022
user=root

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock   ; use a unix:// URL  for a unix socket

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[include]
files = /etc/supervisord.d/*.ini

```

### 4.2 配置具体项目

我们会为不同的程序编写独立的ini配置文件，然后放置到一个统一的路径(比如 /etc/supervisord.d/)下让supervisor读取.具体项目的配置文件 test.celery.ini 如下

``` ini
[group:test_celery]
programs = test_celery.async,test_celery.beat

[program:test_celery.async]
command=/data/test.celery/env/bin/celery worker -A src.app --loglevel=info -Q test_celery_queue
numprocs=1
numprocs_start=0
priority=999
autostart=true
startsecs=3
startretries=3
exitcodes=0,2
stopsignal=QUIT
stopwaitsecs=60
directory=/data/test.celery
user=www-data
stopasgroup=false
killasgroup=false
redirect_stderr=true
stdout_logfile=/data/log/test.celery/test_celery.log
stdout_logfile_maxbytes=250MB
stdout_logfile_backups=10
stderr_logfile=/data/log/test.celery/test_celery.err
stderr_logfile_maxbytes=250MB
stderr_logfile_backups=10
environment=PYTHONPATH='/data/test.celery/';C_FORCE_ROOT="true"

[program:test_celery.beat]
command=/data/test.celery/env/bin/celery beat -A src.app --loglevel=info
numprocs=1
numprocs_start=0
priority=999
autostart=true
startsecs=3
startretries=3
exitcodes=0,2
stopsignal=QUIT
stopwaitsecs=60
directory=/data/test.celery
user=www-data
stopasgroup=false
killasgroup=false
redirect_stderr=true
stdout_logfile=/data/log/test.celery/test_celery.beat.log
stdout_logfile_maxbytes=250MB
stdout_logfile_backups=10
stderr_logfile=/data/log/test.celery/test_celery.beat.err
stderr_logfile_maxbytes=250MB
stderr_logfile_backups=10
environment=PYTHONPATH='/data/test.celery/';C_FORCE_ROOT="true"
```

#### 简单说明

* **test\_celery.async** 和 **test\_celery.beat** 是两个program，分别对应worker和beat，而它们又同属于 **test\_celery** 这个组，这样便于同时管理。
* 注意到command参数了吗？因为我使用了**virtualenv**来隔离每个项目的包环境，所以需要明确指出 **celery命令**所在的目录(如果全局安装了celery就必要了), 这也是为什么上文项目结构中会有一个 **env** 文件夹的原因。
* 使用了虚拟环境之后, 通常需要先激活环境 ```source /data/test.celery/env/bin/activate```
* **environment** 下设置 PYTHONPATH 我们在上文中提到过。总之，你要让Python知道你项目包得位置，设置PYTHONPATH 只是一种方式。

### 4.3 (supervisorctl) 管理程序进程

通过 ```sudo supervisorctl``` 可以进入管理客户端。我们可以使用各种命令管理程序的进程:  

常用的命令有:

- status \<program-name>  查看状态
- restart \<program-name> 重新启动
- start \<program-name>    启动
- stop \<prorgram-name>   停止
- update                                    更新配置

也可以不进入来管理 ，例如每次更新玩配置，我们可以使其快速生效:

``` 
sudo supervisorctl update 
```

​	

## 5. 结束语

上文中只是简单介绍了supervisor 、celery、 celerybeat的简单运用。如果有兴趣的话可以自己去深入了解!

**本篇文章到此结束，原创手打！ **

**人生苦短， 我用python!**



[1]: https://github.com/importcjj/Posts
[2]: http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules

