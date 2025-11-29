
#include "SecurityDLL.h"
#include "AES_CMAC.h"
#include <cstring>
#define SA_API extern "C" __declspec(dllexport)


/*
    Seed-Key DLL for UDS Security Access (0x27)
    -------------------------------------------
    This function implements the Seed-Key calculation required by Vector tools
    and ECUs for authentication. It uses AES-CMAC with different secret keys
    based on the requested security level.

    Inputs:
      - ipSeedArray: Pointer to the seed data provided by the ECU (challenge)
      - iSeedArraySize: Number of bytes in the seed array
      - iSecurityLevel: Security level requested (affects key selection)
      - ipVariant: ECU variant/model string (not used in this implementation)
      - iopKeyArray: Output buffer for the generated key
      - iMaxKeyArraySize: Max bytes available in output buffer
      - oActualKeyArraySize: Reference to store actual generated key length

    Outputs:
      - The generated key is written to iopKeyArray
      - oActualKeyArraySize is set to the number of key bytes produced
      - Return value indicates success or type of error

    Cryptographic keys should be securely managed and stored.
    Replace these example keys with your real secrets in production.
*/

// Example: Symmetric keys for two security levels (normally these are kept secret)
static const unsigned char KEY_LEVEL_1[16] = {
    0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00,
    0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00
};

static const unsigned char KEY_LEVEL_2[16] = {
    0x00, 0xAA, 0x00, 0xAA, 0x00, 0xAA, 0x00, 0xAA,
    0x00, 0xAA, 0x00, 0xAA, 0x00, 0xAA, 0x00, 0xAA
};

/*
    Main Seed-Key algorithm function.
    Called by Vector tools with a seed/challenge from the ECU.
    You must generate the key and return it through the output buffer.
*/

typedef int VKeyGenResultEx;
SA_API VKeyGenResultEx GenerateKeyEx(
    const unsigned char* ipSeedArray,    // Input seed/challenge from ECU
    unsigned int iSeedArraySize,         // Length of the seed
    const unsigned int iSecurityLevel,   // Security level requested by ECU/Vector tool
    const char* ipVariant,               // ECU variant/model string (not used here)
    unsigned char* iopKeyArray,          // Output buffer for generated key
    unsigned int iMaxKeyArraySize,       // Max bytes available in output buffer
    unsigned int& oActualKeyArraySize    // Reference for number of key bytes generated
) {
    // --- Step 1: Input validation ---
    // Check that pointers are not null and buffers are sufficient
    // (AES-CMAC typically produces 16-byte keys)
    if (!ipSeedArray || !iopKeyArray || iSeedArraySize == 0 || iMaxKeyArraySize < 16) {
        // Invalid input, return error code
        return 2;
    }

    // --- Step 2: Select cryptographic key based on security level ---
    // The security level is used to choose which secret key to use for CMAC calculation.
    // You can expand this (with more keys/levels) as needed.
    const unsigned char* selected_key = nullptr;
    if (iSecurityLevel == 0x01) {
        selected_key = KEY_LEVEL_1;
    } else if (iSecurityLevel == 0x03) {
        selected_key = KEY_LEVEL_2;
    } else {
        // Security level not supported; return error
        return 2;
    }

    // --- Step 3: Prepare input for AES-CMAC calculation ---
    // AES-CMAC usually operates on 16-byte blocks. If the seed is shorter,
    // pass only available bytes (or pad if your algorithm requires it).
    // For this example, we use up to 16 bytes.
    unsigned char generated_key[16] = {0}; // Buffer for CMAC result
    size_t input_length = (iSeedArraySize >= 16) ? 16 : iSeedArraySize;

    // --- Step 4: Perform AES-CMAC calculation ---
    // The calculate_aes_cmac function should implement the CMAC calculation.
    // Returns 0 for success, non-zero for error.
    int result = calculate_aes_cmac(selected_key, ipSeedArray, input_length, generated_key);

    if (result != 0) {
        // CMAC calculation failed (could be due to cryptographic error, etc.)
        return 2;
    }

    // --- Step 5: Copy generated key to output buffer ---
    // Only copy up to the available space in the output buffer.
    // In this example, we always produce 16 bytes.
    memcpy(iopKeyArray, generated_key, 16);
    oActualKeyArraySize = 16;

    // --- Step 6: Return success ---
    // Return success code as required by Vector tools.
    return 0;
}

/*
    Notes:
    - This function is what Vector tools will call from your DLL.
    - ipVariant can be used if you need different behavior for ECU variants.
    - Always validate inputs to avoid buffer overflows or crashes.
    - Always keep cryptographic key material secure!
    - Make sure calculate_aes_cmac is implemented per your security requirements.
*/