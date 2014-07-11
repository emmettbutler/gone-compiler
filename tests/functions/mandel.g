/* mandel.e:

   Note: For this program to work under interpretation, you need to provide an accessible
   'putchar' routine in the externals.   See Project8/Solution/exprinterp.py.
 */

extern func putchar(c int) int;
const xmin = -2.0;
const xmax = 1.0;
const ymin = -1.5;
const ymax = 1.5;
const width = 80.0;
const height = 40.0;
const threshhold = 1000;

func in_mandelbrot(x0 float, y0 float, n int) bool {
    var x float = 0.0;
    var y float = 0.0;
    var xtemp float;
    while n > 0 {
        xtemp = x*x - y*y + x0;
        y = 2.0*x*y + y0;
        x = xtemp;
        n = n - 1;
        if x*x + y*y > 4.0 {
            return false;
        }
    }
    return true;
}

func _main() int {
     var dx float = (xmax - xmin)/width;
     var dy float = (ymax - ymin)/height;

     var y float = ymax;
     var x float;
     var r int;
     while y >= ymin {
          x = xmin;
         while x < xmax {
             if in_mandelbrot(x,y,threshhold) {
                   r = putchar(42);
             } else {
            r = putchar(46);
             }
             x = x + dx;
         }
         r = putchar(10);
         y = y - dy;
     }
     return 0;
}
_main();
