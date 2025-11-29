
#include "AES_CMAC.h"
#include <openssl/evp.h>
#include <openssl/core_names.h>
#include <iostream>
#include <cstring>

/*
    calculate_aes_cmac
    -------------------
    Purpose:
      Compute an AES-CMAC over the given input (seed) using the provided key.
      AES-CMAC is commonly used in automotive UDS Security Access (0x27) for
      generating authentication keys from ECU-provided seeds.

    Parameters:
      - key: 16-byte AES key (secret key for CMAC)
      - input: Pointer to seed/challenge data
      - input_length: Length of seed data in bytes
      - output: Buffer to store CMAC result (16 bytes)

    Returns:
      - 0 on success
      - Non-zero on failure

    Notes:
      - Uses OpenSSL EVP_MAC API (modern approach for CMAC).
      - AES-CMAC always produces a 16-byte MAC.
      - Ensure OpenSSL is initialized before calling this function.
      - Caller must validate buffer sizes and handle secrets securely.
*/

int calculate_aes_cmac(
    const unsigned char* key,
    const unsigned char* input,
    size_t input_length,
    unsigned char* output
) {
    try {
        // --- Step 1: Fetch CMAC implementation from OpenSSL ---
        EVP_MAC* mac = EVP_MAC_fetch(NULL, "CMAC", NULL);
        if (!mac) {
            std::cerr << "[CMAC] Failed to fetch CMAC implementation." << std::endl;
            return 1;
        }

        // --- Step 2: Create a new CMAC context ---
        EVP_MAC_CTX* ctx = EVP_MAC_CTX_new(mac);
        if (!ctx) {
            std::cerr << "[CMAC] Failed to create CMAC context." << std::endl;
            EVP_MAC_free(mac);
            return 1;
        }

        // --- Step 3: Specify AES cipher for CMAC ---
        // AES-128-CBC is commonly used for CMAC; key length = 16 bytes.
        OSSL_PARAM params[] = {
            OSSL_PARAM_construct_utf8_string("cipher", (char*)"AES-128-CBC", 0),
            OSSL_PARAM_END
        };

        // --- Step 4: Initialize CMAC with key and cipher ---
        if (!EVP_MAC_init(ctx, key, 16, params)) {
            std::cerr << "[CMAC] Initialization failed." << std::endl;
            EVP_MAC_CTX_free(ctx);
            EVP_MAC_free(mac);
            return 1;
        }

        // --- Step 5: Feed seed data into CMAC ---
        if (!EVP_MAC_update(ctx, input, input_length)) {
            std::cerr << "[CMAC] Update failed." << std::endl;
            EVP_MAC_CTX_free(ctx);
            EVP_MAC_free(mac);
            return 1;
        }

        // --- Step 6: Finalize CMAC and retrieve result ---
        size_t out_len = 0;
        if (!EVP_MAC_final(ctx, output, &out_len, 16)) {
            std::cerr << "[CMAC] Finalization failed." << std::endl;
            EVP_MAC_CTX_free(ctx);
            EVP_MAC_free(mac);
            return 1;
        }

        // --- Step 7: Cleanup ---
        EVP_MAC_CTX_free(ctx);
        EVP_MAC_free(mac);

        // --- Step 8: Validate output length ---
        if (out_len != 16) {
            std::cerr << "[CMAC] Unexpected output length: " << out_len << std::endl;
            return 1;
        }

        return 0; // Success
    }
    catch (const std::exception& ex) {
        std::cerr << "[CMAC] Exception: " << ex.what() << std::endl;
        return 1;
    }
}
