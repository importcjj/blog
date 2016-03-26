Title: 关于Docker的一些杂货
Category: Docker
Tags: Docker
Date: 2016-03-27 03:37:03
Authors: importcjj

#### 如何在外部获取容器的日志?

可以使用`docker logs -f <container>`的方式在宿主机显示容器进程所产生的日志，就像我们使用tail那样。但是如果我们需要访问的并不是容器主进程所记录的日志呢？比如说，现在有一个很简单的web应用，我们选择让他运行在Docker容器里面，web服务器使用了gunicorn，它支持使用参数`--access-file=filename`来将该web应用的访问请求记录到指定的日志中去。当我们需要方便的获取这些访问记录或者实时查看的时候，应该怎么做？

当我们的web应用运行时，gunicorn所记录的日志只存在于docker系统的读写层(容器container)，而不会影响到只读层(镜像image)。如果我们想要较为方便的得到容器中的日志文件，可以使用Docker提供的的`volume`。你可以理解为将宿主系统的文件夹挂载至容器中从而达到实时共享文件夹的目的。

你可以在很多地方指定volume, 比如:

##### 1. Dockerfile 的`VOLUME`命令

```Dockerfile

# Dockerfile

RUN mkdir -p /data/logs/webapp
VOLUME /data/logs/webapp
```
当你使用该Dockerfile去build一个镜像，并使用该镜像来运行了一个容器实例的时候，宿主系统的某个文件夹就会被挂载为该容器的`/data/logs/webapp`文件夹，至于是哪一个文件夹，我们可以通过`docker inspect <container_name>`来查看，在返回的JSON中有一个**Mounts**字段，就像这样:

```json
...
"Mounts": [
        {
            "Name": "1722e5cefd5c077339f69deaaf474c0adea5e3f343c15869802f55cbdeaed743",
            "Source": "/var/lib/docker/volumes/1722e5cefd5c077339f69deaaf474c0adea5e3f343c15869802f55cbdeaed743/_data",
            "Destination": "/data/logs/webapp",
            "Driver": "local",
            "Mode": "",
            "RW": true
        }
    ]
...
```
当我们在宿主机中向`/var/lib/docker/volumes/1722e5cefd5c077339f69deaaf474c0adea5e3f343c15869802f55cbdeaed743/_data`中放文件的时候，对应容器的`/data/logs/webapp`文件夹也会出现这些文件。反之，我们在容器中向该文件夹写日志的时候，在宿主机中也就可以访问这些日志了。

##### 2. docker run 的`-v`参数

作用与VOLUME相同，但是它允许你指定volume的对应关系：

```sh
docker run -v /host/dir/path:/container/dir/path image_name
```
这样一来，宿主机的`/host/dir/path`文件夹就被mount到了容器的`/container/dir/path`，如果容器中原本就有该文件夹， 那么原来的内容会被隐藏。当取消mount后，才可以访问原先的文件。

##### 3. docker run 的`--volumes-from`参数

这个参数主要用于多个容器共享一个volume。有连个容器A指定了volume, 当我们使用命令`docker run --volumes-from A --name B <image>`新建容器B时，B就和A共享volume了。