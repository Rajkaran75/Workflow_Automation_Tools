Seed-Key DLL for UDS Security Access (Service 0x27)
Overview
This project provides a Dynamic-Link Library (DLL) implementation for UDS Security Access (0x27), commonly used in automotive ECUs to unlock restricted diagnostic functions.
The DLL follows the interface expected by Vector tools (CANoe, CANape) and demonstrates how to compute authentication keys from ECU-provided seeds using AES-CMAC.

Features

Implements GenerateKeyEx function as per Vector’s Seed&Key DLL specification.
Uses AES-CMAC for cryptographic key generation.
Modular design for easy integration with diagnostic tools.
Example keys and logic provided for demonstration (replace with OEM-approved algorithms in production).

