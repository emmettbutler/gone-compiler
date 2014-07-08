/* good.e

   This file aims to test all of the valid operator and features
   of simple expr code.
*/

/* Integer operations */

const a = 1;          // Integer constant
var b int = 2;        // Integer variable declaration (with value)
var c int;            // Integer declaration (no value)

c = a + b + 3;        // Assignment to an integer
print c;              // Integer printing.  Outputs 6

print a + b;          // Outputs 3
print a - b;          // Outputs -1
print b * c;          // Outputs 12
print c / b;          // Outputs 2
print +a;             // Outputs 1
print -a;             // Outputs -1

// Test of associativity
print a + b * c;       // Outputs 13

/* Floating point operations */

const fa = 1.0;        // Float constant
var fb float = 2.0;    // Float variable declaration (with value)
var fc float;          // Variable declaration (no value)

fc = fa + fb + 3.0;    // Assignment to an float
print fc;              // Float printing.  Outputs 6.0

print fa + fb;         // Outputs 3.0
print fa - fb;         // Outputs -1.0
print fb * fc;         // Outputs 12.0
print fc / fb;         // Outputs 2.0
print +fa;             // Outputs 1.0
print -fa;             // Outputs -1.0

/* Test strings */
const s1 = "hello";         // String constant
var s2 string = "world";    // String variable
var s3 string;              // String variable (no default)

s3 = s1 + s2;               // String concatenation
print s3;                   // String printing

/* External function declarations */

extern func sin(x float) float;             // from math library
extern func hypot(x float, y float) float;  // from math library
extern func getpid() int;                   // from os library

print sin(0.0);                  // Outputs 0.0
print hypot(3.0, 4.0);           // Outputs 5.0
print getpid();                  // Output varies (an integer)
