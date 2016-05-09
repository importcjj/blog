Title: Golang中三种import方式
Category: Go
Tags: golang, import
Date: 2016-03-27 03:37:03
Authors: importcjj

#### 1. 点方式
有时候会看到如下的方式导入包    ` import( . "fmt" )`

这个点操作的含义就是这个包导入之后在你调用这个包的函数时，你可以省略前缀的包名，也就是前面你调用的`fmt.Println("hello world")`  可以省略的写成`Println("hello world")`

#### 2. 别名方式
别名操作顾名思义可以把包命名成另一个用起来容易记忆的名字。

`import( f "fmt" )`  别名操作调用包函数时前缀变成了重命名的前缀，即`f.Println("hello world")`

#### 3.  _方式  
\_操作其实只是引入该包。当导入一个包时，它所有的init()函数就会被执行，但有些时候并非真的需要使用这些包，仅仅是希望它的init()函数被执行而已。这个时候就可以使用_操作引用该包了。即使用_操作引用包是无法通过包名来调用包中的导出函数，而是只是为了简单的调用其init函数()。

比如 `import (_ "github.com/mattn/go-sqlite3")`只是为了调用该包中的init函数来注册该数据库驱动而已，并需要该包中的其他内容。
