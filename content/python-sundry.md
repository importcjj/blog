Title: Python中一些容易被忽视的东西
Category: Python
Tags: Python
Date: 2016-03-27 03:37:03
Authors: importcjj

### 旨在记录Python标准库中好像很厉害的模块或功能。

##### 1. [functools.partial(func[,*args][, **keywords])](#particial)
##### 2. [globals() and locals()](#globals_and_locals)

#### <a id="particial">functools.partial(func[,*args][, **keywords])</a>
为func的参数指定默认值后返回一个新的函数。比如:

```python
# disable print as the statement
from __future__ import print_function
from functools import partial
from StringIO import StringIO

f = StringIO.StringIO()
print = partial(print, file=f)
print("This will print to f)
# stdout will print nothing!
s = f.getvalue()
# s = "This will print to f"
f.close()
```
原本print函数有个file参数用来指定输出到的目标，例子中我们修改了file参数的默认值，从而重定向print到指定的file对象。虽然这个例子举得好像有点夸张了。

#### <a id="globals_and_locals">globals() and locals()</a>

这两个函数与Python的namespace相关，比如一个函数有它自己的namespace，叫做local namespace，其中存放了只有他自己能够访问的变量和值，包括函数的参数以及在函数内部定义的变量。再比如一个模块有它自己的namespace，叫做global namespace，其中包括了该模块中定义的变量，常数，函数，类，导入的模块。除了这两个之外，还有一个叫build-in的namespace，包含了Python内置函数和异常。

Python解释器按照以下顺序寻找一个变量（或者函数，类等）：

1. local namespace
2. global namespace
3. build-in namespace

注：如果在这三个namespace都不能找到该变量，那么解释器就会抛出`NameError: There is no variable named 'x'`

globals()和locals()返回一个dict，该dict的值是变量名(函数名，类名等)，dict的值就是对应得对象了。在最外层代码，也就是模块层面，locals()和globals()是相等的。

```
>>> globals()
{'__builtins__': <module '__builtin__' (built-in)>, '__name__': '__main__', '__doc__': None, '__package__': None}
>>> locals()
{'__builtins__': <module '__builtin__' (built-in)>, '__name__': '__main__', '__doc__': None, '__package__': None}
```

在Python的一个基于falcon构建的api框架[hug][0]中有一段代码动态创建变量的代码:

```python
for method in HTTP_METHODS:
    method_handler = partial(http, accept=(method, ))
    method_handler.__doc__ = "Exposes a Python method externally as an HTTP {0} method".format(method.upper())
    globals()[method.lower()] = method_handler
```
大致作用是为每个http方法设置一个函数，并将该函数绑定到以该http方法为变量名的变量上。这样能动态创建以指定string为名字的变量名了。
相当于:

```python

get = partial(http, accept=(get,))
get.__doc__ == "Exposes a Python method externally as an HTTP GET method"
# 然后post, put, patch...
```

[0]: https://github.com/timothycrosley/hug