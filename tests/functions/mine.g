extern func putchar(c int) int;

func main() int {
    var i int = 0;
    var j int = 0;
    while i < 10 {
        while j < 20 {
            putchar(42);
            j = j + 1;
        }
        j = 0;
        i = i + 1;
        putchar(10);
    }
    return 0;
}
