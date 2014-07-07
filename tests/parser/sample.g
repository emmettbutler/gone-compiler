/* Sample Expr Program */

    const pi = 3.14159;
    const e = 2.71828;
    const twopi = 2*pi;
    var x int;
    var y int = 23*45;
    var w int;
    x = 42 + y;
    w = -x;

    print twopi;
    print x;
    x = 37;
    print (x/2)*pi;

    const a = "Hello";
    var b string;
    b = a + "World";
    print b;

    print x+z;


    // Extern function declaration
    extern func sin(x float) float;
    print sin(1.0);
    print sin(1.0 + 2.0*3.0);

    // Extern function declaration (multiple arguments)
    extern func hypot(x float, y float) float;
    print hypot(3.0, 4.0);

    // Extern function declaration (no arguments)
    extern func getpid() int;
    print getpid();


