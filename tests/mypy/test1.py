from dependency_injector import providers


class T1:
    pass


class T11(T1):
    pass


class T111(T11):
    pass


class T2:
    pass


class T22(T2):
    pass


class T222(T22):
    pass


class T3:
    pass


class T33(T3):
    pass


class T333(T33):
    pass


class T4:
    pass


class T44(T4):
    pass


class T444(T44):
    pass


class Test1:
    def __init__(self, x1: T1, x2: T2) -> None:
        self.x1 = x1
        self.x2 = x2

    def action(self, x3: T3) -> T4:
        assert isinstance(self.x1, T1) and isinstance(self.x2, T2) and isinstance(x3, T3)
        return T4()


class Test2:
    def __init__(self, x1: T11, x2: T22) -> None:
        self.x1 = x1
        self.x2 = x2

    def action(self, x3: T33) -> T44:
        assert isinstance(self.x1, T11) and isinstance(self.x2, T22) and isinstance(x3, T33)
        return T44()


ok_p1: providers.Provider[Test1] = providers.Factory(Test1, T1())
ok_p11: providers.Provider[Test1] = providers.Factory(Test1, T11())

# TODO: make better error message
err_p1: providers.Provider[Test1] = providers.Factory(Test1, T2())
# TODO: check named args
# err_p11: providers.Provider[Test1] = providers.Factory(Test1, x2=T11())

# ok_p2: providers.Provider[Test1] = providers.Factory(Test1, x2=T2())
# ok_p22: providers.Provider[Test1] = providers.Factory(Test1, x2=T22())

ok_i1: Test1 = ok_p1(T2())
# ok_i11: Test1 = ok_p1(T22())
# ok_i111: Test1 = ok_p1(x2=T2())

# TODO: check partial constructor args
err_i1 = ok_p1(T1())

# ok_r1: T4 = ok_i1.action(T3())
# ok_r11: T4 = ok_i11.action(T3())
# ok_r111: T4 = ok_i111.action(T33())
