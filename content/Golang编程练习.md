Title: Golang编程练习
Category: Go
Tags: Go
Date: 2016-05-10 02:04:13
Authors: importcjj

完整代码 [戳这里](https://github.com/importcjj/fooutils)

##### 1. 验证给定字符串是否为合法身份证号码

算法：前17位纯数字分别乘以相应的因子，然后求和后除以11取余数。使用该余数取得校验字节数组中相位位置的字节与身份证最后一位字节做比较。如果相等即为合法身份证！

```go
package main

import "fmt"
import "strconv"

var (
	Factories    [17]int = [17]int{7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2}
	ValidateBits []byte  = []byte("10X98765432")
)

func IsValidIDCode(id string) bool {
	idBytes := []byte(id)
	if length := len(idBytes); length != 18 {
		return false
	}

	sum := 0
	lastByte := idBytes[17]
	idBytes = idBytes[:17]

	for i, b := range idBytes {
		value, err := strconv.Atoi(string(b))
		if err != nil {
			return false
		}
		sum += value * Factories[i]
	}

	index := sum % 11
	if ValidateBits[index] == lastByte {
		return true
	}

	return false
}

func main() {
	myID := "身份证号码"
	fmt.Println(IsValidIDCode(myID))
}
```

##### 2. 排序之快速排序

快速排序的本质其实很简单: 在一趟排序中，在需要排序的序列中选出一个基准数(pivot), 然后将比它的数放左边， 比它小的放右边。然后采用分治和递归，再去分别对小数序列和大数序列排序。

```go
package main

import "fmt"

func IntQuickSort(slice []int, length int) {
	if length < 2 {
		return
	}

	pivot := slice[0]
	i := 1
	j := length - 1

	// golang中没有while，采用for代替.
	for j > i {
		for ; j > i; j-- {
			if slice[j] <= pivot {
				break
			}
		}
		for ; i < j; i++ {
			if slice[i] > pivot {
				break
			}
		}
		slice[i], slice[j] = slice[j], slice[i]
	}
	slice[0], slice[j] = slice[j], slice[0]

	IntQuickSort(slice[:j], len(slice[:j]))
	IntQuickSort(slice[j+1:], len(slice[j+1:]))
}

func main() {
	// golang中slice是引用类型的，所以在函数内部修改，会改变a
	a := []int{2, 4, 6, 7, 1, 2, 0, 9, 5}
	IntQuickSort(a, len(a))
	fmt.Println(a)
	
	// 有效长度为10， 容量也为10， 默认填充0
	b := make([]int, 10, 10)
	b[5] = 1
	IntQuickSort(b, len(b))
	fmt.Println(b)
}
```
