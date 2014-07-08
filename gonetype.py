# gonetype.py
'''
Gone Type System
================
This file implements the Gone type system.  There is a lot of 
flexibility with the implementation, but start by defining a
class representing a type.

class GoneType(object):
      pass

Concrete types are then created as instances.  For example:

    int_type = GoneType("int",...)
    float_type = GoneType("float",...)
    string_type = GoneType("string", ...)

The contents of the type class is entirely up to you. However,
it must minimally provide information about the following:

   a.  What operators are supported (+, -, *, etc.).
   b.  The result type of each operator.
   c.  Default values for newly created instances of each type
   d.  Methods for type-checking of binary and unary operators
   e.  Maintain a registry mapping builtin type names (e.g. 'int', 'float')
       to type instances.

Don't forget that all of the built-in types need to be registered
with symbol tables and other code that checks for type names. This
might require some coding in 'gonecheck.py'.
'''

Gone Type System
================
This file defines classes representing types.  There is a general
class used to represent all types.  Each type is then a singleton
instance of the type class.

class GoneType(object):
      pass

int_type = GoneType("int",...)
float_type = GoneType("float",...)
string_type = GoneType("string", ...)

The contents of the type class is entirely up to you.  However, you
will minimally need to encode some information about:

   a.  What operators are supported (+, -, *, etc.).
   b.  Default values
   c.  ????
   d.  Profit!

Once you have defined the built-in types, you will need to
make sure they get registered with any symbol tables or
code that checks for type names in 'gonecheck.py'.
'''

class GoneType(object):
    '''
    Class that represents a type in the Gone language.  Types 
    are declared as singleton instances of this type.
    '''
    def __init__(self):
        '''
        You must implement yourself and figure out what to store.
        '''
        pass


# Create specific instances of types. You will need to add
# appropriate arguments depending on your definition of GoneType
int_type = GoneType()
float_type = GoneType()
string_type = GoneType()

# In your type checking code, you will need to reference the
# above type objects.   Think of how you will want to access
# them.

          




