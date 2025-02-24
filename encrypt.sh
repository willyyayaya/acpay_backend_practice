#!/bin/bash

# Check if required commands are available
for cmd in openssl aws base64; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is required but not installed."
        exit 1
    fi
done

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file> <kms_key_arn>"
    echo "Example: $0 secret.txt arn:aws:kms:region:account:key/key-id"
    exit 1
fi

INPUT_FILE="$1"
KMS_KEY_ARN="$2"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found."
    exit 1
fi

# Generate a random 256-bit (32-byte) AES key
echo "Generating AES key..."
AES_KEY=$(openssl rand 32 | base64)

# Encrypt the file with the AES key
echo "Encrypting file..."
openssl enc -aes-256-cbc -salt -in "$INPUT_FILE" \
    -out "${INPUT_FILE}.enc" -base64 -k "$AES_KEY" -pbkdf2

if [ $? -ne 0 ]; then
    echo "Error: File encryption failed."
    exit 1
fi

# Encrypt the AES key with KMS
echo "Encrypting AES key with KMS..."
ENCRYPTED_KEY=$(aws kms encrypt \
    --key-id "$KMS_KEY_ARN" \
    --plaintext "$AES_KEY" \
    --encryption-algorithm RSAES_OAEP_SHA_256 \
    --output text \
    --query CiphertextBlob)

if [ $? -ne 0 ]; then
    echo "Error: KMS encryption failed."
    rm "${INPUT_FILE}.enc"  # Clean up the encrypted file
    exit 1
fi

# Save the encrypted AES key
echo "$ENCRYPTED_KEY" > "${INPUT_FILE}.key"

echo "Encryption complete!"
echo "Encrypted file: ${INPUT_FILE}.enc"
echo "Encrypted key: ${INPUT_FILE}.key"

# Optional: Clean up variables containing sensitive data
AES_KEY=""