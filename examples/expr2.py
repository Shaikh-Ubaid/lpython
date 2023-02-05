from ltypes import i32

def print_int(x: i32):
    if x == 0:
        print(x)
    elif x < 0:
        print("-")
        x *= -1
    digits_cnt: i32 = 0
    while x > 0:
        # push x % 10 onto stack
        digits_cnt += 1
        x = i32(x / 10)
    while digits_cnt > 0:
        # print digit on stack top
        digits_cnt -= 1
    print()

def main0():
    print_int(0)
    print_int(-1)
    print_int(1)
    print_int(-23)
    print_int(23)
    print_int(42523458)
    print_int(-42523458)

main0()
