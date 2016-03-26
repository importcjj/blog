Title: Dockerfile参数学习
Category: Docker
Tags: Docker, Dockerfile
Date: 2016-03-27 03:37:03
Authors: importcjj

#### 镜像和容器

容器是镜像的实例。一个镜像可以对应多个容器。每次使用`docker run <image>`时都会重新创建该镜像的一个容器，我们可以为该命令指定--name <name>来为所产生的容器指定名字:

`docker run -d --name serve ubuntu` 这样根据ubuntu这个镜像产生的容器就叫*serve*。

。当容器运行时，我们对容器的修改只会写人到容器的文件系统，而不会影响到对应镜像。所以， 前一次run形成的改动不会影响到后一次run所创建的容器。想要这些修改对image生效， 可以使用`docker commit <container>`

```
                ├─ 可写层(container)
内核层 - 镜像层 ─ ├─ 可写层(container)
                ├─ 可写层(container)
```
**内核层 - 镜像层 -可写层(container)**
 
#### CMD和ENTRYPOINT的区别

首先两者都可以让你在容器运行的时候执行一条命令，而且这两个字段在Dockerfile中只能指定一次，如果指定多次，那么则以最后一次为准。

再来说两者的区别: 假如我们在运行容器的命令`docker run <image>`中指定了参数。那么CMD指定的命令会被该参数所覆盖, 但是该参数却能为ENTRYPOINT中指定的命令所用。

举个例子:

```Dockerfile
# Dockerfile
# 镜像名: test
...
CMD ["echo", "Hello, CMD!"]
```
当我们使用`docker run test`时，显示`Hello, CMD!`，但当我们使用`docker run test echo hi, everyone!`时， 显示`hi, everyone!`。我们重新指定的echo命令和参数覆盖了原来的echo。 值得注意的是，如果在Dockerfile使用CMD指定命令, 那么在run的时候指定的第一个参数必须时可执行的命令，否则将运行失败！

如果我们使用ENTRYPOINT指定入口命令的话，在docker run命令中指定的参数都会被传递给入口命令.
```Dockerfile
# Dockerfile
# 镜像名: test
...
ENTRYPOINT ["echo", "Hello, CMD!"]
```
运行`docker run test echo hi, everyone!`将得到`Hello, CMD! echo hi, everyone!`

补充:

其实在`run`的时候`ENTRYPOINT`也是可以别覆盖的，通过指定`--entrypoint="xxxx"`参数就可以做到!

#### FROM

指定基础镜像，格式通常为`FROM <image>:<tag>` 例如:
`From ubuntu:latest`
如果本地不存在该镜像，则去Docker Hub中拉取该镜像。

#### MAINTAINER

为该镜像指定作者, 例如:
`MAINTAINER importcjj@ele.me`

#### ENV

设定环境变量， 两种方式:
* ENV \<key> \<value>
* ENV \<key>=\<value>

例如:
* ENV LANG en_US.UTF-8
* ENV PYTHON_VERSION 2.7.6

#### WORKDIR

切换工作目录，类似于cd， 例如:
```Dockerfile
# pwd is /p/dir1
RUN ls
# now cd to /p/dir2
WORKDIR ../dir2
# pwd is /p/dir2
RUN ls
```

#### RUN

可用于运行普通的命令，有两种方式:
* RUN \<command>
* RUN ["executable", "param1", "param2"]

**通常使用第一种**

比如运行相关软件包的安装命令，例如:
* RUN apt-get -y update
* RUN apt-get -y python
* RUN apt-get install -y python-pip
* RUN apt-get install -y python2.7-dev
* RUN pip install flask

#### ADD

将build路径(或者相对位置)的文件，文件夹甚至是远程文件添加至荣区的文件系统的指定位置，可用于设置相关软件的配置文件等例如:
```Dockerfile
ADD requirements.txt /tmp/requirements.txt
RUN pip install -i /tmp/requirements.txt
```

#### VOLUME

将宿主系统的文件夹挂载到容器中指定的文件夹。比如:

```Dockerfile
VOLUME /data/logs
```
此命令的局限性在于无法指定宿主系统的某个文件夹被挂载，只能由docker来分配。可用docker run的`-v src:dest`参数来弥补这一局限性。如果想要查看是哪个文件夹被mount了，使用`docker inspect <container>`，在返回的json结果中的查看**Mounts**这个字段的内容。

#### EXPOSE

指定容器运行时所要监听的端口。虽然配置了EXPOSE, 但我们在运行容器的时候还需要指定端口映射，否则在宿主机中无法访问该端口。 例如:
`docker run -d -p 127.0.0.1:5000:5000`
这样的话我们容器的5000端口就被映射到了宿主机的5000端口。访问宿主机的5000端口，即可访问到容器的5000端口所提供的服务。
同时，多端口的映射也是可以的 `-p 1234-1236:1234-1236/tcp`

#### LABEL

为构建的镜像设置标签
`LABEL <key>=<value> <key>=<value> <key>=<value>`
设置的标签可在 `docker inspect <image>`给出的JSON结果中看到。

#### 例子(来源于github)
```Dockerfile
FROM centos:centos6

RUN cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN yum install -y wget tar gcc zlib zlib-devel openssl openssl-devel unzip mysql-devel python-devel

RUN mkdir /opt/logs
RUN mkdir /usr/src/python
WORKDIR /usr/src/python

ENV LANG en_US.UTF-8
ENV PYTHON_VERSION 2.7.6

RUN curl -SL "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz" | tar xvzf - --strip-components=1
RUN ./configure \
    && make \
    && make install \
    && make clean

RUN sed 's/\/usr\/bin\/python/\/usr\/bin\/python2.6/g' /usr/bin/yum > /usr/bin/yum.tmp \
    && mv /usr/bin/yum.tmp /usr/bin/yum \
    && chmod 755  /usr/bin/yum

ADD . /opt/
WORKDIR /opt

RUN tar zxvf scribed.tar.gz \
    && chown -R root:root scribed \
    && rm -f scribed.tar.gz

RUN curl -SL 'https://bootstrap.pypa.io/get-pip.py' | python
RUN pip install -r requirements.txt \
    && rm -f requirements.txt

RUN easy_install virtualenv \
    && easy_install mysql-connector-python \
    && easy_install MySQL-python

RUN easy_install supervisor \
    && echo_supervisord_conf > /etc/supervisord.conf \
    && echo "[include]" >> /etc/supervisord.conf \
    && echo "files = /etc/supervisord.d/*.conf" >> /etc/supervisord.conf \
    && mkdir -p /etc/supervisord.d \
    && cp gunicorn.conf scribed.conf /etc/supervisord.d/ \
    && rm -f gunicorn.conf scribed.conf Dockerfile
```

#### 更多内容请前往[Docker的官方文档][1]


#### 补充

除了`FROM`, `MAINTAINER`, 'RUN' 和 'AND`四个Dockerfile命令之外, 其他命令都可以在`docker run`时被覆盖! 详见Docker官方文档[docker run reference][2]。

修改Dockerfile的时候，尽量在文件的最后修改(如果允许的话)。这回加快build的速度(缓存的作用：)。因此, 尽量把不轻易变动的部分放在Dockerfile的上方。

如何为正在运行的容器，打开一个新的shell？
* `docker exec -i -t <container_id> bash`
* `docker exec -i -t <container_name> bash`


[1]: https://docs.docker.com/engine/reference/builder/
[2]: https://docs.docker.com/engine/reference/run/