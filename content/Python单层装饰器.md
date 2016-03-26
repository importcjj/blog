Title: Python单层装饰器小记
Category: Python
Tags: 装饰器, Python
Date: 2016-03-26 17:50:50
Authors: importcjj

#### 解释器什么时候处理装饰器？

答: Python解释器加载代码的时候.

例如, sleep.py 代码如下

```python
import functools
import time


def timer(func):
    print("handle decorator")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        rtn = func(*args, **kwargs)
        cost = time.time() - start
        print("cost %f s") % cost
        return rtn
    return wrapper


@timer
def sleep(seconds):
    time.sleep(seconds)
    return seconds
```
以上代码只是定义了一个装饰器和一个使用该装饰器的函数，当运行`python sleep.py`的时候会打印`hanle decorator`。当解释器在加载处理代码的时候遇到了"@"的时候，回去调用timer这个函数，并把sleep这个参数当做参数传给timer。这个过程相当于:

```python
def sleep(seconds):
    time.sleep(seconds)
    return seconds
sleep = timer(sleep)
```

#### 装饰器和闭包？

> 在计算机科学中，闭包（英语：Closure），又称词法闭包（Lexical Closure）或函数闭包（function closures），是引用了自由变量的函数。这个被引用的自由变量将和这个函数一同存在，即使已经离开了创造它的环境也不例外。所以，有另一种说法认为闭包是由函数和与其相关的引用环境组合而成的实体。闭包在运行时可以有多个实例，不同的引用环境和相同的函数组合可以产生不同的实例。
> 

我们不去深究到底什么才是闭包的正确定义。姑且认为就是引用了自由变量的函数。如果在一个内部函数里，对在外部作用域（但不是在全局作用域）的变量进行引用，那么内部函数就被认为是闭包。粗暴的理解为**函数套函数，内层函数引用了外层函数的变量，即使外层函数结束了，内层函数函数仍可以访问该变量**。

在装饰器的用法中，表现为如下方式:

```python
import functools
import time


def timer(func):
    print("handle decorator")
    name = func.func_name

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print name, id(name)
        start = time.time()
        rtn = func(*args, **kwargs)
        cost = time.time() - start
        print("costs %f s") % cost
        return rtn
    return wrapper


@timer
def sleep(seconds):
    time.sleep(seconds)
    return seconds


@timer
def sleep2(seconds):
    time.sleep(seconds)
    return seconds

if __name__ == '__main__':
    print sleep(2)
    print sleep(3)
    print sleep2(2)
    print sleep2(3)

# 运行结果:
handle decorator
handle decorator
# print sleep(2)
sleep 4402047952
costs 2.005124 s
2
# print sleep(3)
sleep 4402047952
costs 3.005203 s
3
# print sleep2(2)
sleep2 4402048048
costs 2.005205 s
2
# print sleep2(3)
sleep2 4402048048
costs 3.000412 s
3
```
可以看到:

1. sleep是可以访问timer函数中的name变量。
2. 同一个函数的多次调用，name变量是同一个(id相同)。
3. 函数**sleep**和**sleep2**所引用的name变量不是同一个，因为timer装饰这两个函数，被调用了两次，声明了两个不同的name变量。

利用以上三点特性，我们可以在装饰器中为被装饰函数开辟一个"存放数据空间"，来看一种应用方式:

```python
import functools
import time


def cache(func):
    caches = {}

    @functools.wraps(func)
    def wrapper(n):
        if n not in caches:
            caches[n] = func(n)
        return caches[n]
    return wrapper


@cache
def fib(n):
    if n < 2:
        return 1
    return fib(n - 1) + fib(n - 2)


def fib2(n):
    if n < 2:
        return 1
    return fib2(n - 1) + fib2(n - 2)


def fib3(n):
    a, b = 1, 1
    for i in xrange(1, n):
        a, b = a + b, a
    return a

if __name__ == "__main__":
    start = time.time()
    for _ in xrange(10000):
        fib(20)
    print "cache fib without cache spends %f s" % (time.time() - start,)

    start = time.time()
    for _ in xrange(10000):
        fib2(20)
    print "no cache fib spends %f s" % (time.time() - start,)

    start = time.time()
    for _ in xrange(10000):
        fib3(20)
    print "fib3 spends %f s" % (time.time() - start,)
    
# 运行结果
cache fib without cache spends 0.003719 s
no cache fib spends 31.374117 s
fib3 spends 0.016529 s
```
递归通常比非递归实现对程序执行的效率影响更大一些，我们带缓冲的递归fib却比非递归版本的fib3耗时更少！

这

#### 类装饰器

我们在创建一个class的时候可以选择重写以下三个方法：

* \_\_new__(cls, *args, **kwargs)   创建实例
* \_\_init__(self, *args, **kwargs)  初始化实例
* \_\_call__(self, *args, **kwargs)  把实例当函数一样调用

```python
import functools
import time


class Timer(object):

    def __init__(self):
        self.names = []

    def __call__(self, func):
        if func.func_name not in self.names:
            self.names.append(func.func_name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print self.names
            start = time.time()
            rtn = func(*args, **kwargs)
            print "%s spends %f s" % (func.func_name, time.time() - start)
            return rtn
        return wrapper

timer = Timer()


@timer
def sleep(seconds):
    time.sleep(seconds)
    return seconds


@timer
def sleep2(seconds):
    time.sleep(seconds)
    return seconds

if __name__ == '__main__':
    sleep(5)
    sleep2(5)
    
＃ 运行结果
['sleep', 'sleep2']
sleep spends 5.000244 s
['sleep', 'sleep2']
sleep2 spends 5.004623 s
```
想要使用类来做装饰器，先要准备一个实例，然后调用这个实例。除了这点要注意外，还要注意的是，用类实现的装饰器，可以让所有被装饰的函数共享变量，这种变量就是实例的内部变量。