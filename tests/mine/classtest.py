class Class2:
    """我的第二个类"""
    career = 'driver456'


class Class1:
    """我的第一个类"""
    career = 'driver123'
    a = 0
    b = 0

    def __init__(self):
        print("我是类Class1的一个实例。")

    def sing(self):
        print("sing a song", self.career)

    def person(self, c=career):
        print("person is a", c)
        self.sing()

    def method2(self):
        Class1.b = 1


class Demo:
    name = 'tom'
    __weight = 100

    def __init__(self, value=0.0):
        self._time = value
        self._unit = 's'

    def myPrint(self):
        print(self.name)

    def myPrint(self, weight=__weight):
        print(weight)

    def myReturn(self):
        return self.name

    @property
    def time(self):
        return str(self._time) + ' ' + self._unit

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError('Time can not be negative.')
        self._time = value


class DemoPro(Demo):
    __height = 180


class DataSet:
    def __init__(self):
        self._images = 1


if "__main__" == __name__:
    d = Demo()
    print(d.time)
    d.time = 1.0
    print(d.time)
