Title: 使用Python制作自定义终端命令
Category: Python
Tags: Python
Date: 2016-03-27 03:37:03
Authors: importcjj

### 介绍

   首先，拿pip举个例子，pip是我们使用较多的python包管理工具。当我们安装pip之后，直接在终端中就可以使用pip这个命令。那你有没有想过这是如何实现的？

      
  其实，pip这个命令最终调用了python所在文件夹bin目录的pip文件。为什么说最终？因为使用系统默认的python安装pip时，可能会在/usr/local/bin或者/usr/bin下创建软链接。如果使用了virtualenv，那么pip文件就在env/bin下。那么pip文件到底是什么呢？答案就是，是一个具有执行权限的python文件，只不过去掉了.py的后缀.
      
   也许你会兴高采烈的去尝试一发，在bin文件下创建xxx.py，打上一句 print “hello world”, 然后去掉.py的后缀, 再使用chmod a+x xxx来赋予它执行的权限。打开终端，敲下xxx。最后你只会得到print: command not found的错误提示。为什么？因为操作系统不知道这是一个py文件。思考一下，我们平时运行py文件都需要打上python xxx.py形式的命令，其实我们告诉了操作系统这是一个python文件（哪怕是有.py后缀），需要使用python解释器来解释运行该文件。现在，我们没有指定解释器了，自然就无法顺利的作为py脚本来运行了，它被错误的认为是shell脚本了。而shell编程中只有echo，没有print命令。
       
   那么我们要做的就是在文件的第一行为该文件指定它的解释器(通过环境变量来获取当前使用的python解释器的路径):
       
    #!/usr/bin/env python

这是一种常见写法，当然可以写成:

    #!/usr/bin/python
    
这样，我们就为这个脚本指定了一个固定的解释器(它的路径是/usr/bin/python)，可能有些时候你需要这样做。但是第一种更加灵活，尤其是在使用virtualenv创建的虚拟环境中，采用第二种写法的脚本将无法导入虚拟环境中安装的依赖包。

### 拓展
安装自己创建的python项目时，如何让安装工具自动在python目录的bin目录下创建自己的命令文件？在python2中，安装一个包，通常需要setup.py这个文件。大致写法如下：

```python
     from setuptools import setup
     setup(
         name=‘project_name’,
          version=‘0.1’,
          ...
          scripts=[‘xxx']
     )
```
以上代码中scripts参数所表示的就是需要在python的bin目录下创建的命令文件在该项目中的路径。

### 实践
环境: python2.7 + mac osx
举个例子，我们现在有个project，目录如下

```
example/

- hello
- setup.py
```

其中, hello是我们写的命令文件，内容如下:

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-

print 'hello world'
```
setup.py的内容如下:

```python
from setuptools import setup
setup(
     name='hahaha',
     version='0.1',
     scripts=[‘./hello']
)
```
因为hello这个文件跟setup.py在同一目录, 所以它相对于setup.py的路径就是./hello 在安装这个简单的项目之前，我们还需要修改一下hello文件到额权限：
          chmod a+x hello

接着安装, `python setup.py` install 或者 `pip install` . 这两种方式随便哪种都可以，安装完成后在终端中输入hello命令试试，有没有显示hello world？

### 结尾
由于hello文件其实是个py文件，所以你可以像写其他py文件一样，修改它，写入任何python代码。当然，说了这么多，提醒一点，并不是所有的python包都是通过上述方式来提供终端命令的，不过这是一种很普遍很简便的方式！