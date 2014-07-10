class GoneType(object):
    '''
    Class that represents a type in the Gone language.  Types
    are declared as singleton instances of this type.
    '''
    def __init__(self, name):
        self.name = name
        self.bin_ops = set()
        self.un_ops = set()
        self.default = 0


class IntType(GoneType):
    def __init__(self):
        self.name = "int"
        self.bin_ops = {"+", "-", "*", "/", "<", ">", "<=", ">=", "==", "!="}
        self.un_ops = {"+", "-"}
        self.default = 0


class FloatType(GoneType):
    def __init__(self):
        self.name = "float"
        self.bin_ops = {"+", "-", "*", "/", "<", ">", "<=", ">=", "==", "!="}
        self.un_ops = {"+", "-"}
        self.default = 0.0


class StringType(GoneType):
    def __init__(self):
        self.name = "string"
        self.bin_ops = {"+", "==", "!="}
        self.un_ops = {}
        self.default = ""


class BoolType(GoneType):
    def __init__(self):
        self.name = "bool"
        self.bin_ops = {"!=", "==", "||", "&&"}
        self.un_ops = {"!"}
        self.default = "false"


class ErrorType(GoneType):
    def __init__(self):
        self.name = "<error>"
        self.bin_ops = {}
        self.un_ops = {}
        self.default = None


int_type = IntType()
float_type = FloatType()
string_type = StringType()
bool_type = BoolType()
error_type = ErrorType()
