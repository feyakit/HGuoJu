#import "HGuoJuCoreAnchor.h"
#include <stddef.h>

extern char *HGuoJuRequest(char *input);
extern void HGuoJuFree(char *value);

void ZgjEnsureCoreLinked(void) {
    char *result = HGuoJuRequest(NULL);
    if (result != NULL) {
        HGuoJuFree(result);
    }
}
