#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Usage: %s <input>", argv[0]);
        return 1;
    }
    
    FILE* f = fopen(argv[1], "r");
    if (!f) {
        perror("fopen");
        return 1;
    }
    
    char buf[1024];
    size_t len = fread(buf, 1, sizeof(buf), f);
    fclose(f);
    
    // Simple test logic to generate different coverage
    if (len >= 1) {
        if (buf[0] == 'A') {
            printf("First byte is A\n");
            if (len >= 2) {
                if (buf[1] == 'B') {
                    printf("Second byte is B\n");
                    if (len >= 3) {
                        if (buf[2] == 'C') {
                            printf("Third byte is C\n");
                        }
                    }
                }
            }
        }
    }
    
    return 0;
}