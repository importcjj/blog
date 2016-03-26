Title: Python的metaclass小记
Category: Python
Tags: metaclass, Python
Date: 2016-03-26 17:50:50
Authors: importcjj


使用metaclass的时候可以使用**metaclass**的`__new__`和`__init__`去改变所定义的类的相关属性，因为这两个方法是在类定义的时候被调用，他们所需的参数也与使用`type(name, bases, dict)`动态声明类相同。而是用**metaclass**的`__call__`可以影响我们所声明的类产生实例的过程，因为当我们使用class_name()去产生实例的时候，相当于call了这个class，而这个class又是metaclass的实例，所以其实调用了metaclass的\_\_call__

注意: 通过`super`来调用父类的`__new__`时，第一个参数需要是该class，这点是不同于调用`__init__`等其他父类方法的。因为`__new__`是个静态方法。还有一个小问题就是当父类是object的时候，也就是调用`object.__new__()`只传一个cls参数就可以了，至于为什么，请戳[here](https://mail.python.org/pipermail/python-dev/2008-February/076854.html)
和[here](http://bugs.python.org/issue1683368)。 如果你重写了`__new__`而没有重写`__init__`，那么给`object.__new__`传额外的参数会直接报错, 如果两个都重写了会报出**DeprecationWarning**，可以继续运行。

```python
class Meta(type):

    def __new__(meta, cls_name, base_clses, cls_attrs):
        print "============Meta_new=============="
        print "meta", meta
        print "class name", cls_name
        print "base classes", base_clses
        print "class attrs", cls_attrs
        instance = super(Meta, meta).__new__(meta, cls_name, base_clses, cls_attrs)
        print "=============Meta_new============"
        return instance

    def __init__(cls_obj, cls_name, base_clses, cls_attrs):
        print "============Meta_init============"
        print 'class obj', cls_obj
        print "class name", cls_name
        print "base classes", base_clses
        print "class attrs", cls_attrs
        print "============Meta_init==========="

    def __call__(cls_obj,  *args, **kwargs):
        print "=============Meta_call=========="
        print "class obj", cls_obj
        instance = super(Meta, cls_obj).__call__(*args, **kwargs)
        print "=============Meta_call=========="
        return instance


class Foo(object):
    __metaclass__ = Meta

    def __new__(cls):
        print cls
        print 'Foo.__new__'
        return super(Foo, cls).__new__(cls)

    def __init__(self):
        print 'Foo.__init__'

if __name__ == '__main__':
    Foo()
    print type.__call__(Foo)
```

输出
```
============Meta_new==============
meta <class '__main__.Meta'>
class name Foo
base classes (<type 'object'>,)
class attrs {'__module__': '__main__', '__metaclass__': <class '__main__.Meta'>, '__new__': <function __new__ at 0x1091ad578>, '__init__': <function __init__ at 0x1091b9578>}
=============Meta_new============
============Meta_init============
class obj <class '__main__.Foo'>
class name Foo
base classes (<type 'object'>,)
class attrs {'__module__': '__main__', '__metaclass__': <class '__main__.Meta'>, '__new__': <function __new__ at 0x1091ad578>, '__init__': <function __init__ at 0x1091b9578>}
============Meta_init===========
=============Meta_call==========
class obj <class '__main__.Foo'>
<class '__main__.Foo'>
Foo.__new__
Foo.__init__
=============Meta_call==========
<class '__main__.Foo'>
Foo.__new__
Foo.__init__
<__main__.Foo object at 0x1091b6910>
```