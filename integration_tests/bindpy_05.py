from lpython import ccall, Pointer, i32, i64, empty_c_void_p, CPtr, pointer
import os

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def Py_Initialize():
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def Py_DecodeLocale(s: str, p: CPtr) -> CPtr:
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def PySys_SetArgv(n: i32, args: Pointer[CPtr]):
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def Py_FinalizeEx() -> i32:
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def PyUnicode_FromString(s: str) -> CPtr:
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def PyImport_Import(name: CPtr) -> CPtr:
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def PyObject_GetAttrString(m: CPtr, s: str) -> CPtr:
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def PyTuple_New(n: i32) -> CPtr:
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def PyObject_CallObject(a: CPtr, b: CPtr) -> CPtr:
    pass

@ccall(header="Python.h", c_shared_lib="python3.10", c_shared_lib_path=f"{os.environ['CONDA_PREFIX']}/lib")
def PyLong_AsLongLong(a: CPtr) -> i32:
    pass

def my_f():
    pName: CPtr; pModule: CPtr; pFunc: CPtr; pArgs: CPtr; pValue: CPtr

    pName = PyUnicode_FromString("bindpy_05_module")
    assert bool(pName), "Failed to convert to unicode string bindpy_05_module\n"

    pModule = PyImport_Import(pName)
    assert bool(pModule), "Failed to load python module bindpy_05_module\n"

    pFunc = PyObject_GetAttrString(pModule, "my_f")
    assert bool(pFunc), "Cannot find function my_f\n"

    pArgs = PyTuple_New(0)
    pValue = PyObject_CallObject(pFunc, pArgs)
    assert bool(pValue), "Call to my_f failed\n"

    ans: i32 = PyLong_AsLongLong(pValue)
    print("Ans is", ans)
    assert ans == 5


def main0():
    Py_Initialize()
    argv1: CPtr = Py_DecodeLocale("", empty_c_void_p())
    PySys_SetArgv(1, pointer(argv1, i64))

    my_f()

    assert(Py_FinalizeEx() >= 0), "BindPython: Unknown Error in FinalizeEx()\n"

main0()
