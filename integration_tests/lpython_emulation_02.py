from lpython import i32, dataclass
from numpy import array

@dataclass
class X:
    a: i32 = 123
    b: bool = True
    c: i32[:] = array([1, 2, 3])
    d: i32[:] = array([4, 5, 6])

def main0():
    x: X = X()
    print(x)
    assert x.a == 123
    assert x.b == True
    assert x.c.sum() == 6
    assert x.d.sum() == 15

main0()
