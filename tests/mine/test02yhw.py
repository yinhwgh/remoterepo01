class Person:
    __country = 'China'

    @staticmethod
    def getCountry():
        return Person.__country

    def __init__(self, name, age):
        self.name = name
        self.age = age
        print('this is a person!')

    @property
    def country(self):
        return self._country


class Teacher(Person):
    def __init__(self, name, age):
        super().__init__(name, age)
        print('this is a teacher!')


class Student:
    def __init__(self):
        self.abc = None

    @property
    def age(self):
        print('获取属性时执行的代码')
        return self.abc

    @age.setter
    def age(self, a):
        print('设置属性时执行的代码')
        self.abc = a


class Singleton(object):
    __instance = None
    __first_init = False

    def __new__(cls, age, name):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, age, name):
        if not self.__first_init:
            self.age = age
            self.name = name
            Singleton.__first_init = True


if __name__ == '__main__':
    p1 = Person('Tom', '20')
    print(Person.getCountry())
    print(p1.getCountry())

