Title: Python的单例实现
Category: Python
Tag: singleton, decorator
Date: 2016-04-26 16:10:27
Author: importcjj


#### 由于实现的方式很多，先来3种。

#### 1. 类实例实现的单例装饰器

```python
import functools

class Singleton(object):
  
  	def __init__(self):
    	self.instances = {}
    
  	def __call__(self, cls):
    	@functools.wraps(cls)
    	def wrapper(*args, **kwargs)
      		cls_name = cls.__name__
      		if not self.instances.get(cls_name):
        		self.instances[cls_name] = cls(*args, **kwargs)
      		return self.instances[cls_name]
    	return wrapper
    
singleton = Singleton()

# 用法
@singleton
class Test(object):
	pass

if __name__ == '__main__':
  	t1 = Test()
  	t2 = Test()
  	print(t1, t2)
  	print(type(t1), type(t2))
  	assert t1 == t2

# 这种方式有一个缺点，就是Test这个类会变成一个function, 
# 这样的话就无法使用instance等方式了。
```


#### 2. 类实现的单例装饰器

```python

class Singleton(object):

	def __init__(self, cls):
		self.cls = cls
		self.__class__ = cls
		self.cls_instance = None
	
	def __call__(self, *args, **kwargs):
		if not self.cls_instance:
			self.cls_instance = self.cls(*args, **kwargs)
		return self.cls_instance
		
@Singleton
class Test(object):
	pass


if __name__ == '__main__':
	print(Test)
	t1 = Test()
	t2 = Test()
	print(t1, t2)
	assert t1 == t2

# 这种方式Test其实已经是single的一个实例了
# 缺点和第一种方式一样，Test已经不是原来的Test了
# 而t1, t2却还是原来的Test的实例
# 对于这种方式我还存有疑虑，但是又说不出来
# 总感觉怪怪的
```

#### 3. metaclass元类

关于metaclss的介绍请看我写的另一篇[小记](<Python的metaclass小记.md>)

```python

class Singleton(type):
	
```
