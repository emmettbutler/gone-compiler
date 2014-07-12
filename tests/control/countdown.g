/* countdown.e */

var n int = 100000000;

while n > 0 {
     if (n / 1000000)*1000000 == n {
         print n;
     }
     n = n - 1;
}
