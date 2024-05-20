---
title: "go-multierror"
linkTitle: "go-multierror"
weight: 23
date: 2022-05-30
description: Provides a mechanism for representing a list of error values as a single error.

---

[github.com/hashicorp/go-multierror](https://github.com/hashicorp/go-multierror)

## Problem with wrapping errors

There is no way to preserve error type while wrapping with `fmt.Errorf`.

For example, standard way to implement such functionality is verbose.

```go
package main

import (
	"errors"
	"fmt"
)

var ErrInvalidInputParameter = errors.New("invalid input parameter")
var ErrExternalServiceUnavailable = errors.New("external service unavailable")

type ErrUnathorized struct {
	ErrUnderlying error
}

func (e *ErrUnathorized) Error() string {
	return fmt.Sprintf("unathorized: %v", e.ErrUnderlying)
}

type ErrTooManyRequests struct {
	ErrUnderlying error
}

func (e *ErrTooManyRequests) Error() string {
	return fmt.Sprintf("too many requests: %v", e.ErrUnderlying)
}

func main() {
	_, err := callExternalService()

	var errUnathorized *ErrUnathorized
	if errors.As(err, &errUnathorized) {
		fmt.Println("execute logic if unathorized")
	}

	var errTooManyRequests *ErrTooManyRequests
	if errors.As(err, &errTooManyRequests) {
		fmt.Println("execute logic if too many requests")
	}
}

func callExternalService() (string, error) {
	return "", &ErrUnathorized{
		ErrUnderlying: ErrExternalServiceUnavailable,
	}
}
```

## go-multierror solution

```go
package main

import (
	"errors"
	"fmt"

	"github.com/hashicorp/go-multierror"
)

var ErrInvalidInputParameter = errors.New("invalid input parameter")
var ErrExternalServiceUnavailable = errors.New("external service unavailable")

var ErrUnathorized = errors.New("unathorized")
var ErrTooManyRequests = errors.New("too many requests")

func main() {
	_, err := callExternalService()

	if errors.Is(err, ErrUnathorized) {
		fmt.Println("execute logic if unathorized")
	}

	if errors.Is(err, ErrTooManyRequests) {
		fmt.Println("execute logic if too many requests")
	}
}

func callExternalService() (string, error) {
	return "", multierror.Append(ErrExternalServiceUnavailable, ErrUnathorized)
}
```

## Examples

- https://github.com/takeoff-com/products-audit/blob/e5d74adc76616add062e8580e67c9ad34031de7c/cloud-functions/get-product-changes/auth.go#L114
