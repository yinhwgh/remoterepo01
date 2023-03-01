def mydecorator(func):
    def wrap(pa):
        print("do something before function...")
        func(pa)
        print("do something after function...")

    return wrap


def hi(name='123'):
    print(name)


hi = mydecorator(hi)
hi('456')

# @mydecorator
# def hi(name='123'):
#     print(name)

# hi('456')
