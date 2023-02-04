def print_int(x: i32):
    if x < 0:
        print("-", end="")
    if x == 0:
        print(x)
    while x > 0:
        print(x % 10)
        x /= 10


def main0():
    x: i32
    x = (2+3)*5
    print(x)

main0()
