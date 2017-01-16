Title: Golang接口型函数
Category: Go
Tags: Go
Date: 2017-01-16 11:22:11
Author: importcjj

```go

package main

import (
	"fmt"
)

type Handler interface {
	Do(k, v interface{})
}

type HandlerFunc func(k, v interface{})

func (f HandlerFunc) Do(k, v interface{}) {
	f(k, v)
}

func Each(m map[interface{}]interface{}, h Handler) {
	for k, v := range m {
		h.Do(k, v)
	}
}

func EachFunc(m map[interface{}]interface{}, f func(k, v interface{})) {
	Each(m, HandlerFunc(f))
}

func SayHello(name, age interface{}) {
	fmt.Printf("Hello, I am %s, %d years old!\n", name, age)
}

func main() {
	students := make(map[interface{}]interface{})
	students["Marry"] = 20
	students["Tom"] = 23
	EachFunc(students, SayHello)
}

```
