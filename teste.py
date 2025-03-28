def mdc(a, b):
    while b:
        a, b = b, a % b
    return a


print(mdc(9,17))