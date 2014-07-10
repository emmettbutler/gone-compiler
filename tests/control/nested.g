// nested.e
//
// Nested loops

var i int = 0;
var j int = 0;

while i < 3 {
    j = 0;
    while j < 3 {
        print i;
        print j;
        j = j + 1;
    }
    i = i + 1;
}
