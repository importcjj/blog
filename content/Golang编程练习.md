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

以前学的一种实现使用while循环，老是在right, left等于的时候搞不清楚啊。在参考了wiki百科之后，发现以下写法清晰易懂。
允许随便选取一个基准（不过我写的时候，默认使用第一位了), 先把基准放置到最后一位，然后遍历前n-1个数，把小于基准数的数往前放，同时使用一个游标来记录。遍历完之后，将基准数交换到游标处。自此，基准数之前全是小于基准数的，之后都是小于等于基本数的。然后分别继续递归。

```go
package main

import "fmt"

func main() {
	a := []int{5, 5, 4, 3, 2, 3, 5, 1, 1, 5}

	IntQuickSort(a, 0, 9)
	fmt.Println(a)
}



func IntQuickSort(slice []int, left, right int) {

	if right - left <= 1 {
		return
	}

	// 默认将第一位作为基准位
	pivotIndex := left
	
	// 把基准交换到最后一位
	slice[pivotIndex], slice[right] = slice[right], slice[pivotIndex]

	storeIndex := left
	for i := left; i < right; i++ {
		if slice[i] < slice[right] {
			slice[storeIndex], slice[i] = slice[i], slice[storeIndex]
			storeIndex ++
		}
	}
	slice[storeIndex], slice[right] = slice[right], slice[storeIndex]

	IntQuickSort(slice, left, storeIndex-1)
	IntQuickSort(slice, storeIndex+1, right)
}

```

##### 3. 排序至归并排序

![merge sort](http://7xsw69.com1.z0.glb.clouddn.com/Merge-sort-example-300px.gif)

上图非常清楚的表现了归并排序的过程: 先不停的对半分组，直到分成一个数字一组， 然后相邻的两组作比较，归并成有序的一组，不断向上归并。

```go
package main

import "fmt"

func IntMergeSort(slice []int, left, right int) {
	if left >= right {
		return
	}
	cache := make([]int, len(slice))
	intMergeSort(slice, cache, left, right)
}

func intMergeSort(slice, cache []int, left, right int) {
	length := right - left
	if length <= 0 {
		return
	}

	middle := length>>1 + left

	left1, right1 := left, middle
	left2, right2 := middle+1, right

	intMergeSort(slice, cache, left1, right1)
	intMergeSort(slice, cache, left2, right2)

	index := left
	for left1 <= right1 && left2 <= right2 {
		if slice[left1] < slice[left2] {
			cache[index] = slice[left1]
			left1++
		} else {
			cache[index] = slice[left2]
			left2++
		}
		index++

	}

	for left1 <= right1 {
		cache[index] = slice[left1]
		left1++
		index++
	}
	for left2 <= right2 {
		cache[index] = slice[left2]
		left2++
		index++
	}

	for i := left; i <= right; i++ {
		slice[i] = cache[i]
	}
}

func main() {
	slice := []int{4, 5, 6, 7, 1, 2, 3, 9}
	IntMergeSort(slice)
	fmt.Println(slice)
}
```
