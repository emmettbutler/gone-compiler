/* good_func.e

   Try calling some external functions.
*/

/* External function declarations */

extern func sin(x float) float;             // from math library
extern func hypot(x float, y float) float;  // from math library
extern func getpid() int;                   // from os library

print sin(0.0);                  // Outputs 0.0
print hypot(3.0, 4.0);           // Outputs 5.0
print getpid();                  // Output varies (an integer)
