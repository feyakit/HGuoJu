package main

/*
#include <stdlib.h>
*/
import "C"
import (
	"hguoju/native/core"
	"unsafe"
)

//export HGuoJuRequest
func HGuoJuRequest(input *C.char) *C.char {
	if input == nil {
		return C.CString(`{"ok":false,"error":"请求为空"}`)
	}
	return C.CString(core.NativeRequest(C.GoString(input)))
}

//export HGuoJuFree
func HGuoJuFree(value *C.char) { C.free(unsafe.Pointer(value)) }

func main() {}
