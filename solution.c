#define _XOPEN_SOURCE
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

char *read(FILE *file, char *buffer) {
    if (fgets(buffer, 1000, file) != NULL) {
        char *start = buffer;
        while (isspace((unsigned char)*start)) {
            start++;
        }
        char *end = start + (strlen(start) - 1);
        while ((end > start) && isspace((unsigned char)*end)) {
            end--;
        }
        *(end + 1) = '\0';
        return start;
    } else {
        return NULL;
    }
}

int main(int argc, char *argv[]) {

    FILE *file = fopen(argv[1], "r");
    char buffer[1000];
    char *timestamp;
    struct tm tm;
    time_t prev_time = 0;
    time_t current_time = 0;
    int first = 1;

    while ((timestamp = read(file, buffer)) != NULL) {
        memset(&tm, 0, sizeof(struct tm));
        char *format = "%Y/%m/%d %H:%M:%S";
        if (strptime(timestamp, format, &tm) == NULL) {
            return 1;
        } else {
            tm.tm_isdst = -1;
            current_time = mktime(&tm);
            if (!first) {
                printf("%d\n", (int)difftime(current_time, prev_time));
                prev_time = current_time;
                continue;
            }
            first = 0;
            prev_time = current_time;
        }
    }

    fclose(file);
    return 0;
}
