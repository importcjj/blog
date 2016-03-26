Title: Python yield小记
Category: Python
Tags: yield, 生成器, Python
Date: 2016-03-27 03:37:03
Authors: importcjj

####yeild
*yield* 一般搭配函数来定义一个Generator(生成器)

一个简单的例子:

```python
def f():
	print "Today is 7.21"
	yield 6
```
*f()* 将会返回一个Generator, 而非像普通函数一样执行。想要使用生成器的话(比如 i)需要使用i.next() (与next(i)等效) 和i.send(value)。

```python
>>> i = f()
>>> i
<generator object f at 0x1041e7dc0>
>>> i.next()
Today is 7.21
6
>>> i.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```
生成器调next()或send()方法后会执行函数体内的语句，执行到yield语句后停止, 并返回yield语句的参数，上例中就是 6。再次使用next()或send()会从停止处继续执行，由于之后已经没有yield了，所以会raise StopTteration异常。

有时候可能会遇到这样的情况

```python
def f():
	m = 5
	m = yield 6
	print "m = ", m
```
上例中 m 会得到（yield 6）这个式子的值。那么，这个值是多少呢？取决于i.next()和i.send(value)。如果是next，则是None。send的话就是value。

*can't send non-None value to a just-started generator* 第一次调用只能是
i.next()或者i.send(None)

这里需要注意一点，第一次next会在执行(yield 6)后停止，并不会执行m的赋值(重新绑定，毕竟python不太一样)。m的值是轮到下一个next或send来改变的。

```python
>>> def f():
...     m = 5 
...     m = yield 6
...     print "m = ", m
... 
>>> i = f()
>>> i.next()
6
>>> i.send(7)
m =  7
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

####使用
```python
def fibonacci(i):
    """关于斐波那契数列的生成器
    """
    if i < 0:
        raise ValueError, i
    if i == 0:
        yield 0

    count = 0
    a, b = 0, 1
    while count <= i:
        yield a
        a, b = b, a + b
        count += 1

>>> for i in fibonacci(13):
...     print i,
... 
0 1 1 2 3 5 8 13 21 34 55 89 144
>>> for i in fibonacci(-1):
...     print i,
... 
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "_yield.py", line 5, in fibonacci
    raise ValueError, i
ValueError: -1
>>> for i in fibonacci(0):
...     print i,
... 
0
>>> for i in fibonacci(1):
...     print i
... 
0 1
```
随便写了一个关于斐波拉切数列的生成器，并且遍历了它。

####终止生成器
```python
fib = fibonacci(6)
fib.close()
```
```python
fib.throw(GeneratorExit)
# GeneratorExit 继承自 BaseException
```
使用这两种方法之后，再去访问生成器的方法，会触发StopIteration异常。遍历的话也不会返回有效值。

####最后
关于yield暂时只想到这些，以后可能补充。生成器不一定还能通过别的方式定义。比如

```python
(i for i in range(6))
```