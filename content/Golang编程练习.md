Title: Golang编程练习
Category: Go
categories: Go
Date: 2016-05-10 02:04:13
Authors: importcjj

完整代码 [戳这里](https://github.com/importcjj/fooutils)

##### 1. 验证给定字符串是否为合法身份证号码

算法：前17位纯数字分别乘以相应的因子，然后求和后除以11取余数。使用该余数取得校验字节数中相位位置的字节与省份证最后一位字节做比较。如果相等即为合法身份证！

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

	var sum int = 0
	var lastByte byte = idBytes[17]
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
