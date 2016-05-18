Title: Greenlet: 轻量级并发编程
Category: Python
Tags: concurrent, gevent
Date: 2016-05-18 14:07:45

#### 动机

greenlet这个包拆分自Stackless。Stackless是一个CPython的版本，支持一种叫做tasklets的微线程。Tasklets会以一种伪并发的方式运行(通常运行在单个或者一些系统级的线程中)，它们之间通过channels来同步数据。

一个greenlet，从另一方面来说，依然是一种很原始的没有隐式调度的微线程。换句话说，就是协程(coroutine)。这在你想要完全控制代码的运行时是非常有用的。你可以在greenlet之上构建采用自定义调度方式的微线程。然而，使用greenlet来制作先进的控制流结构是很有用的。举个例子，我们可以重新创造生成器。和Python自带的生成器所不同的是，我们的生成器可以调用网状的方法，而且这些网状的方法也可以yield出值。(另外，你不需要再使用**yield**这个关键词了）

以下greenlets官方给出的两种实现，可选择跳过。

##### 1. 简单的生成器

```python
import unittest
from greenlet import greenlet


class genlet(greenlet):

    def __init__(self, *args, **kwds):
        self.args = args
        self.kwds = kwds

    def run(self):
        fn, = self.fn
        fn(*self.args, **self.kwds)

    def __iter__(self):
        return self

    def __next__(self):
        self.parent = greenlet.getcurrent()
        result = self.switch()
        if self:
            return result
        else:
            raise StopIteration

    # Hack: Python < 2.6 compatibility
    next = __next__


def Yield(value):
    g = greenlet.getcurrent()
    while not isinstance(g, genlet):
        if g is None:
            raise RuntimeError('yield outside a genlet')
        g = g.parent
    g.parent.switch(value)


def generator(func):
    class generator(genlet):
        fn = (func,)
    return generator

# ____________________________________________________________


class GeneratorTests(unittest.TestCase):
    def test_generator(self):
        seen = []

        def g(n):
            for i in range(n):
                seen.append(i)
                Yield(i)
        g = generator(g)
        for k in range(3):
            for j in g(5):
                seen.append(j)
        self.assertEqual(seen, 3 * [0, 0, 1, 1, 2, 2, 3, 3, 4, 4])
```

##### 2. 网状调用生成器

```python
import unittest
from greenlet import greenlet


class genlet(greenlet):

    def __init__(self, *args, **kwds):
        self.args = args
        self.kwds = kwds
        self.child = None

    def run(self):
        fn, = self.fn
        fn(*self.args, **self.kwds)

    def __iter__(self):
        return self

    def set_child(self, child):
        self.child = child

    def __next__(self):
        if self.child:
            child = self.child
            while child.child:
                tmp = child
                child = child.child
                tmp.child = None

            result = child.switch()
        else:
            self.parent = greenlet.getcurrent()
            result = self.switch()

        if self:
            return result
        else:
            raise StopIteration

    # Hack: Python < 2.6 compatibility
    next = __next__


def Yield(value, level=1):
    g = greenlet.getcurrent()

    while level != 0:
        if not isinstance(g, genlet):
            raise RuntimeError('yield outside a genlet')
        if level > 1:
            g.parent.set_child(g)
        g = g.parent
        level -= 1

    g.switch(value)


def Genlet(func):
    class Genlet(genlet):
        fn = (func,)
    return Genlet

# ____________________________________________________________


def g1(n, seen):
    for i in range(n):
        seen.append(i + 1)
        yield i


def g2(n, seen):
    for i in range(n):
        seen.append(i + 1)
        Yield(i)

g2 = Genlet(g2)


def nested(i):
    Yield(i)


def g3(n, seen):
    for i in range(n):
        seen.append(i + 1)
        nested(i)
g3 = Genlet(g3)


def a(n):
    if n == 0:
        return
    for ii in ax(n - 1):
        Yield(ii)
    Yield(n)
ax = Genlet(a)


def perms(l):
    if len(l) > 1:
        for e in l:
            # No syntactical sugar for generator expressions
            [Yield([e] + p) for p in perms([x for x in l if x != e])]
    else:
        Yield(l)
perms = Genlet(perms)


def gr1(n):
    for ii in range(1, n):
        Yield(ii)
        Yield(ii * ii, 2)

gr1 = Genlet(gr1)


def gr2(n, seen):
    for ii in gr1(n):
        seen.append(ii)

gr2 = Genlet(gr2)


class NestedGeneratorTests(unittest.TestCase):
    def test_layered_genlets(self):
        seen = []
        for ii in gr2(5, seen):
            seen.append(ii)
        self.assertEqual(seen, [1, 1, 2, 4, 3, 9, 4, 16])

    def test_permutations(self):
        gen_perms = perms(list(range(4)))
        permutations = list(gen_perms)
        self.assertEqual(len(permutations), 4 * 3 * 2 * 1)
        self.assertTrue([0, 1, 2, 3] in permutations)
        self.assertTrue([3, 2, 1, 0] in permutations)
        res = []
        for ii in zip(perms(list(range(4))), perms(list(range(3)))):
            res.append(ii)
        self.assertEqual(
            res,
            [([0, 1, 2, 3], [0, 1, 2]), ([0, 1, 3, 2], [0, 2, 1]),
             ([0, 2, 1, 3], [1, 0, 2]), ([0, 2, 3, 1], [1, 2, 0]),
             ([0, 3, 1, 2], [2, 0, 1]), ([0, 3, 2, 1], [2, 1, 0])])
        # XXX Test to make sure we are working as a generator expression

    def test_genlet_simple(self):
        for g in [g1, g2, g3]:
            seen = []
            for k in range(3):
                for j in g(5, seen):
                    seen.append(j)
            self.assertEqual(seen, 3 * [1, 0, 2, 1, 3, 2, 4, 3, 5, 4])

    def test_genlet_bad(self):
        try:
            Yield(10)
        except RuntimeError:
            pass

    def test_nested_genlets(self):
        seen = []
        for ii in ax(5):
            seen.append(ii)
```

#### 举例

我们来思考一个程序，用户可以在一个类终端控制台中输入命令来控制该程序。假设命令是一个字符一个字符的输入。在这样一个系统中，通常会存在如下一个循环:

```python
def process_commands(*args):
    while True:
        line = ''
        while not line.endswith('\n'):
            line += read_next_char()
        if line == 'quit\n':
            print "are you sure?"
            if read_next_char() != 'y':
                continue    # ignore the command
        process_command(line)
```
如果现在假设你想要将这个程序插入到用户界面中。大部分的用户界面工具都是基于事件驱动的，它们会在用户输入一个字符后调用回调函数。在这种设定下，编写上述代码所需的read\_next\_char()函数是非常难的，将会有如下两个冲突的函数:

```python
def event_keyworn(key):
	??
	
def read_next_char():
	??应该等待下一个event_keydown()函数的调用
```
显然，上述情况在串行运行是不可能的。你也许想到了使用多个线程来完成。使用Greenlets作为替代方法，可以免去关联锁和程序退出的相关问题。你可以在程序运行主干中分裂出一个greenlet来专门运行process_commands()函数，你可以使用如下方式来交换用户的按键情况：

```python
def event_keydown(key):
    # 跳转至g_processor, 并且把用户所按键发送给g_processor
    g_processor.switch(key)
    
def process_commands():
	while True:
	    line = ''
	    while not line.endswith('\n'):
	        line += read_next_char()
	    if line == 'quit\n':
	        print "are you sure?"
	        if read_next_char() != 'y':
	            continue    # ignore the command
	    process_command(line)

def read_next_char():
    # 在这个例子里，g_self就是g_processor
    g_self = greenlet.getcurrent()
    # 跳转到父greenlet(主greenlet)中，等待下一个按键
    next_char = g_self.parent.switch()
    return next_char

g_processor = greenlet(process_commands)
g_processor.switch(*args)   # input arguments to process_commands()

gui.mainloop()
```
在这个例子中，执行过程如下: 当read\_next\_char()被调用时，身处于g\_processor这个greenlet中，所以它的父greenlet也就是派生g\_processor的根greenlet。当它显示切换回父greenlet的时候，程序会重新回到顶层继续GUI事件监听循环。当事件监听循环回调event\_keydown()函数的时候, 又切换回g\_processor，这意味着程序会跳转到目标greenlet之前被挂起的地方继续执行-在这个例子里，将会跳转会read\_next\_char()函数中调用switch()的地方继续执行，并且在event\_keydown()中调用switch()时所给的参数key会被做为返回值，并赋值给变量next\_char。

注意，read\_next\_char()函数在被挂起和恢复时，它的调用栈会得到保护。所以它会在process\_commands()中的不同位置返回，这主要取决于它原先被调用的位置。这使程序的执行逻辑以一种很好的控制流得以保持。我们不需要完全重写process\_commands()来使其转化为状态机。

#### 使用

##### 简介

一个greenlet其实是一个独立的微伪线程。把它想象成一个小型的frame栈。最外层的frame就是你调用的初始函数，最里层的frame就是greenlet目前正停留的frame。在你使用greenlets的时候，就是通过创建大量的这种栈，并且在它们之间跳跃执行。跳跃(切换)永远都是显式的。一个greenlet必须显式切换至目标greenlet，这样会使前者的执行被挂起，而目标greenlet会在之前挂起的地方被恢复过来继续执行。greenlets之间的跳跃被称为**切换**。

当你创建了一个greenlet，它会的到一个初始的空栈；当第一次切换到这个greenlet的时候，它开始执行一个指定的函数，在这个函数中又可能会调用其他函数，切换至其他greenlet。最终当最外层的函数执行完毕后，整个greenlet的调用栈再次变空，那么这个greenlet就死了。greenlet也可能死于未被捕获的异常。

举个例子:

```python
from greenlet import greenlet

def test1():
    print 12
    gr2.switch()
    print 34

def test2():
    print 56
    gr1.switch()
    print 78

gr1 = greenlet(test1)
gr2 = greenlet(test2)
gr1.switch()
```

最后一行跳转至函数test1，打印出12。又跳转至函数test2，打印了56。重新跳转会test1，打印了34。 然后test1所在的greenlet执行完成并且死亡。此时，程序回到最开始的gr1.switch()继续执行。注意，78将永远不会被执行。

#### 父级

让我们看看当某个greenlet死亡的的时候，程序会如何执行。每一个greenlet都会有一个父greenlet。顾名思义，父greenlet就是分裂出子greenlet的greenlet(不过可以随时通过greenlet.parent来修改某一个greenlet的父greenlet)。当greenlet结束的时候，程序会回到他的父greenlet继续执行。这样，所有的greenlet形成树结构。树的根节点其实是隐式的**主greenlet**，所以不在用户自定义的greenlet中执行的代码都会在主greenlet中被执行。

在上面的例子中，gr1和gr2的父greenlet都是最外层的主greenlet，不论是它们中谁结束了，程序就会回到主greenlet继续执行。

greenlet未被捕获的异常也会往外抛给父级greenlet。举个例子，如果上面例子中的函数test2包含一个拼写错误，那么所产生的**NameError**异常会干死gr2，程序便会直接回到主greenlet执行。而traceback会包含test2，但不会包含test1。记住，switch不是调用，而是在多个并行的栈容器之间切换执行。父级表示了它的栈在逻辑上是在当前greenlet的下方的。

#### 实例

`greenlet.greenlet`是greenlet类型， 它支持以下操作:

`greenlet(run=None, parent=None)`
创建新的greenlet对象(不会运行)。`run`参数执行需要执行的函数，`parent`指定它的父级greenlet，默任的话就是当前的greenlet。

`greenlet.getcurrent()`
返回当前所在的greenlet（即调用该函数的greenlet)

`greenlet.GreenletExit`
这个特定的异常并不会被往外抛给其父级greenlet；使用它可以杀死一个greenlet。

`greenlet`类也可以被继承。greenlet的run属性一般是在greenlet创建时被设置，调用`run`可以启动该greenlet。但当你定义greenlet的子类时，重写其`run`方法比在构造函数中传入`run`参数来的有意义。

#### 切换

greenlet之间的切换发生在某个greenlet的switch函数被调用的时候，亦或是某个greenlet结束的时候(程序会返回父级greenlet继续执行)。在切换期间，一个对象或异常会被发送给目标greenlet。这可以作为一种方便的方法在greenlet之间传递信息。比如:

```python
def test1(x, y):
    z = gr2.switch(x+y)
    print z

def test2(u):
    print u
    gr1.switch(42)

gr1 = greenlet(test1)
gr2 = greenlet(test2)
gr1.switch("hello", " world")
```

上述程序将会打印"hello, world"和42。值的注意的是，函数test1和函数test2的参数不是在greenlet被创建时所提供，而是在第一次切换到它们执行时提供。

`g.switch(*args, **kwargs)`
将执行权切换给greenlet **g**, 并将指定参数发送给它。特别的是，如果g还没有启动，那么此时g将会启动。

**greenlet之死**
如果greenlet的run函数执行完了，函数的返回值将会被发送给其父级。如果run函数被异常所终止，则异常也会被抛给其父级(除非是greenlet.GreenletExit异常，该异常会被捕获，函数执行结束并返回父级)。

除了上述之外，目标greenlet通常接收对象作为调用之前已被挂起的greenlet的switch()函数的返回值。实际上，尽管对于switch()函数的调用不会立即返回，但是仍然会在未来的某个时刻返回(可能是别的greenlet切换时给出的参数，也可能是之前switch的greenlet的函数返回值)。此时，程序会回到之前被挂起的位于对于switch()函数的调用处。这表示 x = g.switch(y) 会把y发送给greenlet **g**，然后过段时间之后，会接收到一个对象并赋值给x。

注意，对于任何已死greenlet的切换操作都会走到它们的父辈，或者父父辈，以此类推。最后的父级greenlet就是整棵树的根节点**main**greenlet，因为它永远不会死亡。


#### greenlet的属性和方法
`g.switch(*args, **kwargs)`
切换至greenlet **g**。

`g.run`
greenlet启动时将会执行的函数。当greenlet **g** 启动后该属性将不复存在。

`g.parent`
父级greenlet。该属性可修改，但是不允许形成循环父子结构。

`g.gr_frame`
The current top frame, or None.
当前顶层frame，没有则是None。

`g.dead`
如果greenlet **g**已经执行结束了，则返回True。

`bool(g)`
如果greenlet **g**还活着，则返回True，结束活着还未开始都是False。

`g.throw([typ, [val, [tb]]])`
切换至greenlet **g**，不过会立刻在g中抛出给定的异常。如果没有指定任何参数，那么默认抛出`greenlet.GreenletExit`，那么g就结束了。调用这个函数就相当于下面的过程:

```python
def raiser():
    raise typ, val, tb
g_raiser = greenlet(raiser, parent=g)
g_raiser.switch()
```
注意，上述代码对于`greenlet.GreenletExit`无效，因为该异常不会被抛给父级greenlet **g**。

#### greenlets和Python线程

greenlet可以和Python的线程结合使用；这种情况下，每一个线程将包含一个主greenlet和大量子greenlet，形成树形结构。对于属于不同线程的greenlets，混合或者切换操作是不可能的。

#### greenlet的垃圾回收

如果对于一个greenlet对象的所有引用都不存在了(包括来自其他greenlet的parent属性的引用)，然后就没有办法再切换到这个greenlet了。这种情况下，`GreenletExit`异常就会在该greenlet中产生，这是一个greenlet唯一的一种异步获取执行权的情况。你可以使用`try:finally:`语句块来清理该greenlet所占有的资源。这个特性同时也支持那种使用死循环接收并处理数据的编码风格。当对于greenlet的最后一个引用被干掉后，死循环就会自动终止了。

通过在某处保存对于某个greenlet的新引用可以认为这个greenlet可以正常死亡或重新恢复。只要捕获并忽略`GreenletExit`异常就可以让这个greenlet进入死循环。

Greenlet不参与垃圾回收；greenlet中的循环引用将不会被发现，循环保存对于greenlet的引用可能会导致内存泄露。

Tracing support
Standard Python tracing and profiling doesn’t work as expected when used with greenlet since stack and frame switching happens on the same Python thread. It is difficult to detect greenlet switching reliably with conventional methods, so to improve support for debugging, tracing and profiling greenlet based code there are new functions in the greenlet module:

`greenlet.gettrace()`
Returns a previously set tracing function, or None.
greenlet.settrace(callback)
Sets a new tracing function and returns a previous tracing function, or None. The callback is called on various events and is expected to have the following signature:

```python
def callback(event, args):
    if event == 'switch':
        origin, target = args
        # Handle a switch from origin to target.
        # Note that callback is running in the context of target
        # greenlet and any exceptions will be passed as if
        # target.throw() was used instead of a switch.
        return
    if event == 'throw':
        origin, target = args
        # Handle a throw from origin to target.
        # Note that callback is running in the context of target
        # greenlet and any exceptions will replace the original, as
        # if target.throw() was used with the replacing exception.
        return
```
如果事件类型既有**'switch'**又有**'throw'**, 那么对于参数元组args的解包就非常重要。这样的话，API就可以像`sys.settrace()`那样被扩展为更多的事件类型。
