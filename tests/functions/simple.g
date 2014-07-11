print 84;
var a int = 8 + 5 * 5;

func test(x int) int {
    x = 3;
    if true {
        return 1;
    } else {
        return 2;
    }
}

print 96;
var b int = test(7);
