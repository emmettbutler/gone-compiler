/* parsetest3.e

   Add support for var and const declarations.  Also add support for
   user-defined identifiers in expression.s
*/

const pi = 3.14159;
const twopi = 2.0*pi;

var x int;
var y int = 23*45;

print x+y;
print twopi;
