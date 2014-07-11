/* A simple conditional */

var a int = 2;
var b int = 3;

if a < b {
    if false {
        print a;
    }
}

if a > b {
   print a;
} else {
  print b;
}

func test() int {
    return 1;
}
print a;
print b;
