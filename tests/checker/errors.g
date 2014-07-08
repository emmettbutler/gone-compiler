/* errors.e

   A sample program with a wide variety of semantic errors that must be catch by
   your compiler.

*/

/* Type errors on operators */

print 2 + 2.5;               // Type error : int + float
print 2 + "4";               // Type error : int + string

/* Checks for unsupported operations on strings */

print "Hello" - "World";     // Type error: Unsupported operator - for type string
print "Hello" * "World"; 
print "Hello" / "World";
print +"Hello";
print -"Hello";

/* Assignment to an undefined variable */
b = 2;

/* Assignment to a constant */
const c = 4;
c = 5;

/* Assignment type error */
var d int;
d = 4;       // Good
d = 4.5;     // Bad

/* Bad type names */
var e foo;
var f d;

/* Variable declaration type error */
var g int = 2.5;

/* Propagation of types in expressions */
var h int;
var i float;
var j int = h * i;

/* Undefined variable in an expression */
print 2 + x;

/* Bad location */
print 2 + int;

/* Duplicate definition */

var d float;
var int int;

/* Calling a nonexistent function */

print blah(2,3);

/* Calling an identifier that's not actually a function */

var nonfunc int;
print nonfunc(2);

/* Calling a function with wrong number of args */

extern func hypot(x float, y float) float;
print hypot(2.0);
print hypot();

/* Calling a function with bad types */
print hypot(2,3);

/* Assigning to a bad variable type */

var r int;
r = hypot(2.0, 3.0);

/* What happens if a function is used as data */

print hypot;







