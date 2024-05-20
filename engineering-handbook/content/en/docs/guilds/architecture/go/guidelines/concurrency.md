---
title: "Concurrency"
linkTitle: "Concurrency"
weight: 8
date: 2021-12-17
description: >
  Policies and recommendations for concurrency 
---

## Done channel pattern

Go to [Go Concurrency Patterns: Pipelines and cancellation](https://go.dev/blog/pipelines) to get more details

Example of usage

``` golang
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())

	wg := sync.WaitGroup{}

	wg.Add(2)

	go func() {
		defer wg.Done()
		for {
			select {
			case <-time.After(10 * time.Second):
				fmt.Println("doing some work")
			case <-ctx.Done():
				fmt.Println("abort!")
				return
			}
		}
	}()

	go func() {
		defer wg.Done()
		time.Sleep(21 * time.Second)

		cancel()
	}()

	wg.Wait()
	fmt.Println("finish")
}

```

Output gonging to be:
- doing some work
- doming some work
- abort!
- finish
