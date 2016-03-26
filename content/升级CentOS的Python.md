Title: 升级CentOS的Python版本
Category: CentOS
Tags: CentOS, Python, 运维
Date: 2016-03-26 17:50:50
Authors: importcjj


服务器(centos)上默认的python版本是python2.6，但是平时使用的是2.7，故手动升级一下吧。

下载最新版本[Python-2.7.10](https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz)

```bash
wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz

tar -zxvf Python-2.7.10.tgz
```
提前安装依赖

```bash
yum install zlib
yum install zlib-devel
yum install openssl -y
yum install openssl-devel -y
```

配置编译安装替换

```
cd Python-2.7.10
./configure --prefix=/usr/local/python2.7
```
修改配置

```
cd Python-2.7.10
vim Modules/Setup
去掉456行左右
#zlib zlibmodule.c -I$(prefix)/include -L$(exec_prefix)/lib -lz的注释
```
Go on...

```bash
make
make install
rm /usr/bin/python
ln -s /usr/local/bin/python2.7 /usr/bin/python
```
修复yum

```bash
vim /usr/bin/yum
将
#!/usr/bin/python
替换为
#!/usr/bin/python2.6(根据版本而定)
```
安装pip

```bash
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
```
这里比较坑的一点是，以后安装的带有命令行命令的第三方库都不能直接在终端通过命令调用，而是需要使用绝对路径或者在/usr/bin中创建链接才能正常使用。关于这点我暂时还不知道如何优雅的解决它。