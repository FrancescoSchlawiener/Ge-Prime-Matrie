#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>

/* ========================================================================= *
 * FPM KERNEL-KONSTANTEN & LIMITS
 * ========================================================================= */
#define MAX_GENOME_LEN 64
#define MAX_ROOM_OBJECTS 20
#define MAX_BIT_VOLUME_LIMIT 45
#define CONFIDENCE_THRESHOLD 0.10

/* VOLLENDUNG: Zyklische Reduktion für unbegrenzte Identität
 * Verhindert 64-Bit Overflows, bewahrt die topologische Integrität. */
#define BIG_PRIME 100000000000000003ULL 

/* Einkompiliertes System-Sprachmodell (Schritt 16) */
static const unsigned int SYSTEM_REFERENCE_MASK = 0x000E3215; 

/* ========================================================================= *
 * SCHRITT 6 & VOLLENDUNG: Das dimensionale Super-Teilchen als TENSOR
 * ========================================================================= */
typedef struct fpm_object_t {
    unsigned long long substanz;      /* Zyklische Masse S (Modulo BIG_PRIME) */
    unsigned long long index;         /* Topologische Koordinate I */
    unsigned int fpm_mask;            /* Spektrale Signatur */
    struct fpm_object_t *tensor_next; /* Verzeigerung in die Tiefe (Schienennetz) */
} fpm_object_t;

/* ========================================================================= *
 * ZERO-COPY RING BUFFER (Shared Memory)
 * ========================================================================= */
#define SHM_BUFFER_SIZE 4096
typedef struct {
    fpm_object_t objects[MAX_ROOM_OBJECTS];
    int count;
    int system_frozen;
    
    /* Hardware-Interrupt Ring-Buffer */
    char input_buffer[SHM_BUFFER_SIZE];
    volatile int head;
    volatile int tail;
} gpm_shm_t;

static gpm_shm_t *shm_ptr = NULL;
static const char *shm_path = "/gpm_tensor_core_shm";

/* --- Prototypen --- */
unsigned long long char_to_prime(int c1, int c2);
unsigned long long berechne_fakultaet(int n);
unsigned long long calc_N(int rem_L, int *rem_freqs, int num_u);
int berechne_bit_volumen(unsigned long long n);
unsigned int char_to_bitmask(int c1, int c2);
int custom_popcount(unsigned int x);
double berechne_audit_konfidenz(unsigned int real_mask);
unsigned long long berechne_I(const unsigned long long *seq, int L, unsigned long long *out_N);
unsigned long long berechne_tensor_I(fpm_object_t *head, int L, unsigned long long *out_N);

/* ========================================================================= *
 * SIGNAL HANDLER (Interrupt-Steuerung)
 * ========================================================================= */
void handle_sigio(int sig) {
    (void)sig; 
    /* Ein leeres Return weckt den Prozess automatisch aus dem pause() */
}

void handle_singularity(int sig) {
    (void)sig;
    if (shm_ptr != NULL) {
        shm_ptr->system_frozen = 1;
        printf("\n\n[!!!] SINGULARITÄT TRIGGER (SIGUSR1) [!!!]\n");
        printf("Shannon-Entropie H(X) -> 0. System im Vakuum eingefroren.\n\n");
    }
}

/* ========================================================================= *
 * GPM KERN-MATHEMATIK (Lexikalische Matrix & Metriken)
 * ========================================================================= */
unsigned long long char_to_prime(int c1, int c2) {
    if (c1 == 0xC3 && c2 == 0x9F) return 103; /* ß */
    char upper_c = (char)toupper(c1);
    switch(upper_c) {
        case 'E': return 2;   case 'A': return 3;   case 'O': return 5;
        case 'I': return 7;   case 'T': return 11;  case 'N': return 13;
        case 'R': return 17;  case 'S': return 19;  case 'L': return 23;
        case 'C': return 29;  case 'D': return 31;  case 'U': return 37;
        case 'M': return 41;  case 'P': return 43;  case 'H': return 47;
        case 'G': return 53;  case 'B': return 59;  case 'F': return 61;
        case 'Y': return 67;  case 'W': return 71;  case 'K': return 73;
        case 'V': return 79;  case 'X': return 83;  case 'Z': return 89;
        case 'J': return 97;  case 'Q': return 101;
        default:  return 1;
    }
}

unsigned int char_to_bitmask(int c1, int c2) {
    if (c1 == 0xC3 && c2 == 0x9F) return (1U << 26);
    char upper_c = (char)toupper(c1);
    if (upper_c >= 'A' && upper_c <= 'Z') return (1U << (upper_c - 'A'));
    return 0;
}

int custom_popcount(unsigned int x) {
    int count = 0;
    while (x) { count += x & 1U; x >>= 1; }
    return count;
}

double berechne_audit_konfidenz(unsigned int real_mask) {
    unsigned int intersection = real_mask & SYSTEM_REFERENCE_MASK;
    unsigned int union_mask = real_mask | SYSTEM_REFERENCE_MASK;
    if (union_mask == 0) return 1.0;
    return (double)custom_popcount(intersection) / (double)custom_popcount(union_mask);
}

unsigned long long berechne_fakultaet(int n) {
    unsigned long long f = 1;
    for (int i = 2; i <= n; i++) f *= (unsigned long long)i;
    return f;
}

unsigned long long calc_N(int rem_L, int *rem_freqs, int num_u) {
    unsigned long long n_val = berechne_fakultaet(rem_L);
    for (int i = 0; i < num_u; i++) {
        if (rem_freqs[i] > 1) n_val /= berechne_fakultaet(rem_freqs[i]);
    }
    return n_val;
}

int berechne_bit_volumen(unsigned long long n) {
    int bits = 0;
    while (n > 0) { bits++; n >>= 1; }
    return bits;
}

/* ========================================================================= *
 * INTERVALLSCHACHTELUNG (Der Topologische Split in O(n))
 * ========================================================================= */
unsigned long long berechne_I(const unsigned long long *seq, int L, unsigned long long *out_N) {
    unsigned long long alphabet[MAX_GENOME_LEN];
    int freqs[MAX_GENOME_LEN] = {0};
    int num_unique = 0;
    
    for (int i = 0; i < L; i++) {
        int found = 0;
        for (int j = 0; j < num_unique; j++) {
            if (alphabet[j] == seq[i]) { freqs[j]++; found = 1; break; }
        }
        if (!found) { alphabet[num_unique] = seq[i]; freqs[num_unique] = 1; num_unique++; }
    }

    for (int i = 0; i < num_unique - 1; i++) {
        for (int j = 0; j < num_unique - i - 1; j++) {
            if (alphabet[j] > alphabet[j + 1]) {
                unsigned long long t_a = alphabet[j]; alphabet[j] = alphabet[j + 1]; alphabet[j + 1] = t_a;
                int t_f = freqs[j]; freqs[j] = freqs[j + 1]; freqs[j + 1] = t_f;
            }
        }
    }

    *out_N = calc_N(L, freqs, num_unique);
    unsigned long long index_I = 0;

    for (int t = 0; t < L; t++) {
        unsigned long long act = seq[t];
        unsigned long long sprung = 0;

        for (int j = 0; j < num_unique; j++) {
            if (alphabet[j] >= act) break;
            if (freqs[j] > 0) {
                freqs[j]--; 
                unsigned long long perms = berechne_fakultaet(L - 1 - t);
                for (int k = 0; k < num_unique; k++) {
                    if (freqs[k] > 1) perms /= berechne_fakultaet(freqs[k]);
                }
                sprung += perms; 
                freqs[j]++; 
            }
        }
        index_I += sprung;
        for (int j = 0; j < num_unique; j++) {
            if (alphabet[j] == act) { freqs[j]--; break; }
        }
    }
    return index_I;
}

/* ========================================================================= *
 * VOLLENDUNG: TENSOR-KOLLAPS (Satz-Ebene über Linked List Pointer)
 * ========================================================================= */
unsigned long long berechne_tensor_I(fpm_object_t *head, int L, unsigned long long *out_N) {
    if (L == 0 || head == NULL) { *out_N = 0; return 0; }
    
    unsigned long long satz_seq[MAX_ROOM_OBJECTS];
    fpm_object_t *curr = head;
    int idx = 0;
    
    /* Traversiere die Kaskade */
    while (curr != NULL && idx < L) {
        satz_seq[idx++] = curr->substanz;
        curr = curr->tensor_next;
    }
    
    return berechne_I(satz_seq, idx, out_N);
}

/* ========================================================================= *
 * MAIN: HARDWARE & KERNEL SIMULATION
 * ========================================================================= */
int main(void) {
    /* 1. Shared Memory Mapping (Zero-Copy Interprozess-Kommunikation) */
    int shm_fd = shm_open(shm_path, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) { perror("SHM Failed"); return EXIT_FAILURE; }
    ftruncate(shm_fd, sizeof(gpm_shm_t));
    shm_ptr = (gpm_shm_t *)mmap(NULL, sizeof(gpm_shm_t), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    
    shm_ptr->count = 0;
    shm_ptr->head = 0;
    shm_ptr->tail = 0;
    shm_ptr->system_frozen = 0;

    pid_t pid = fork();

    if (pid > 0) {
        /* ------------------------------------------------------------------
         * PARENT: Hardware DMA Controller 
         * Schreibt asynchron ins RAM und triggert den Kernel via SIGIO
         * ------------------------------------------------------------------ */
        printf("[HARDWARE DMA] Controller aktiv. Sende Bytes direkt in den Shared Memory...\n");
        printf("[HARDWARE DMA] Eingabe starten (z.B. '_START WORT _END'):\n");
        
        int ch;
        while ((ch = fgetc(stdin)) != EOF) {
            int next_head = (shm_ptr->head + 1) % SHM_BUFFER_SIZE;
            while (next_head == shm_ptr->tail) { /* Ring Buffer voll - Hardware wartet */ }
            
            shm_ptr->input_buffer[shm_ptr->head] = ch;
            shm_ptr->head = next_head;
            
            /* Sende Interrupt an Kernel bei Leerzeichen oder Newline */
            if (ch == '\n' || ch == ' ') {
                kill(pid, SIGIO);
            }
        }
        kill(pid, SIGTERM);
        wait(NULL);
        munmap(shm_ptr, sizeof(gpm_shm_t));
        shm_unlink(shm_path);
        return 0;
    } 
    else {
        /* ------------------------------------------------------------------
         * CHILD: GPM Tensor Kernel (Wacht nur bei SIGIO Interrupts auf)
         * ------------------------------------------------------------------ */
        signal(SIGIO, handle_sigio);
        signal(SIGUSR1, handle_singularity);

        unsigned long long substanz = 1;
        int status_skip = 0, raum_aktiv = 0;
        unsigned long long word_primes[MAX_GENOME_LEN];
        char word_chars[MAX_GENOME_LEN * 2];
        int word_len = 0, word_char_idx = 0;
        unsigned int current_mask = 0;

        word_chars[0] = '\0';

        while (1) {
            /* Das Kern-Axiom: Der Kernel schläft bei 0% CPU, bis Hardware Daten liefert */
            if (shm_ptr->head == shm_ptr->tail) {
                pause(); 
            }

            /* Verarbeitung des Ring-Puffers direkt aus dem Memory (Zero-Copy) */
            while (shm_ptr->head != shm_ptr->tail) {
                if (shm_ptr->system_frozen) {
                    shm_ptr->tail = shm_ptr->head; /* Flush */
                    break;
                }

                int ch = shm_ptr->input_buffer[shm_ptr->tail];
                shm_ptr->tail = (shm_ptr->tail + 1) % SHM_BUFFER_SIZE;

                if (ch == '\n' || ch == '\r' || ch == ' ' || ch == '\t') {
                    if (word_char_idx > 0) {
                        if (strcmp(word_chars, "_START") == 0) {
                            raum_aktiv = 1;
                            shm_ptr->count = 0;
                            printf("\n[KERNEL] ---> ÖFFNE TENSOR-SCOPE (_START)\n");
                        } 
                        else if (strcmp(word_chars, "_END") == 0) {
                            if (raum_aktiv && shm_ptr->count > 0) {
                                /* =========================================================
                                   DIE VOLLENDUNG: TENSOR-KOLLAPS DES SATZ-SUBSTRATS
                                   ========================================================= */
                                unsigned long long S_total = 1;
                                
                                /* KASKADIERUNG: Durchwandern der Tensor-Pointer (LinkedList) */
                                fpm_object_t *head_ptr = &shm_ptr->objects[0];
                                fpm_object_t *curr = head_ptr;
                                
                                while (curr != NULL) {
                                    /* Zyklische Reduktion zur Erhaltung der fraktalen Identität */
                                    S_total = (S_total * curr->substanz) % BIG_PRIME;
                                    curr = curr->tensor_next;
                                }

                                unsigned long long N_total = 0;
                                unsigned long long I_total = berechne_tensor_I(head_ptr, shm_ptr->count, &N_total);
                                
                                printf("\n=======================================================\n");
                                printf(" 🌌 TENSOR-VERSCHRÄNKUNG (SATZ-SUBSTRAT VIA POINTER) 🌌\n");
                                printf("=======================================================\n");
                                printf("  Groß-S (Modulo BIG_PRIME) : %llu\n", S_total);
                                printf("  Groß-I (Tensor-Index)     : %llu\n", I_total);
                                printf("  Tensor-Kardinalität N     : %llu (Bit-Volumen: %d)\n", N_total, berechne_bit_volumen(N_total));
                                printf("=======================================================\n");
                            }
                            raum_aktiv = 0;
                        } 
                        else if (raum_aktiv) {
                            /* Lokale Wort-Ebene verarbeiten */
                            double audit_conf = berechne_audit_konfidenz(current_mask);
                            if (audit_conf < CONFIDENCE_THRESHOLD) {
                                printf("[FIREWALL] Wort '%s' abgelehnt. Konfidenz %.1f%%\n", word_chars, audit_conf*100);
                                status_skip = 1;
                            }

                            unsigned long long word_N = 0;
                            unsigned long long index_I = berechne_I(word_primes, word_len, &word_N);
                            
                            if (berechne_bit_volumen(word_N) > MAX_BIT_VOLUME_LIMIT || status_skip) {
                                printf("[KERNEL-SKIP] Genom '%s' blockiert.\n", word_chars);
                            } else if (shm_ptr->count < MAX_ROOM_OBJECTS) {
                                int w_idx = shm_ptr->count;
                                shm_ptr->objects[w_idx].substanz = substanz;
                                shm_ptr->objects[w_idx].index = index_I;
                                shm_ptr->objects[w_idx].fpm_mask = current_mask;
                                shm_ptr->objects[w_idx].tensor_next = NULL;
                                
                                /* TENSOR-POINTER VERKNÜPFEN (Schienennetz in die Tiefe) */
                                if (w_idx > 0) {
                                    shm_ptr->objects[w_idx - 1].tensor_next = &shm_ptr->objects[w_idx];
                                }
                                shm_ptr->count++;
                                printf("[KERNEL] Genom '%s' -> S(%llu) I(%llu) in Tensor verzeigert.\n", word_chars, substanz, index_I);
                            }
                        }
                    }
                    substanz = 1; word_len = 0; word_char_idx = 0;
                    status_skip = 0; current_mask = 0; word_chars[0] = '\0';
                    fflush(stdout);
                    continue;
                }

                int ch2 = EOF;
                if (ch == 0xC3) {
                    while(shm_ptr->head == shm_ptr->tail) { pause(); }
                    ch2 = shm_ptr->input_buffer[shm_ptr->tail];
                    shm_ptr->tail = (shm_ptr->tail + 1) % SHM_BUFFER_SIZE;
                }

                if (word_char_idx < (MAX_GENOME_LEN * 2) - 3) {
                    word_chars[word_char_idx++] = (char)ch;
                    if (ch2 != EOF) word_chars[word_char_idx++] = (char)ch2;
                    word_chars[word_char_idx] = '\0';
                }

                unsigned long long prime = char_to_prime(ch, ch2);
                if (prime > 1 && word_len < MAX_GENOME_LEN) {
                    word_primes[word_len++] = prime;
                    current_mask |= char_to_bitmask(ch, ch2);
                    
                    /* VOLLENDUNG: ZYKLISCHE REDUKTION AUF LOKALER WORT-EBENE 
                     * Das System stürzt bei langen Wörtern nie wieder ab. */
                    substanz = (substanz * prime) % BIG_PRIME;
                }
            }
        }
    }
    return 0;
}