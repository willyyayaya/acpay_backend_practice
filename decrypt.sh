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
    echo "Usage: $0 <encrypted_file> <kms_key_arn>"
    echo "Example: $0 secret.txt.enc arn:aws:kms:region:account:key/key-id"
    echo "Note: The script expects <encrypted_file>.key to exist with the encrypted AES key"
    exit 1
fi

ENCRYPTED_FILE="$1"
KMS_KEY_ARN="$2"
BASE_NAME="${ENCRYPTED_FILE%.enc}"
KEY_FILE="${BASE_NAME}.key"

# Check if files exist
if [ ! -f "$ENCRYPTED_FILE" ]; then
    echo "Error: Encrypted file '$ENCRYPTED_FILE' not found."
    exit 1
fi

if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Key file '$KEY_FILE' not found."
    exit 1
fi

# Read the encrypted key
ENCRYPTED_KEY=$(cat "$KEY_FILE")

# Debug info
echo "Debug: Encrypted key length (base64): $(echo -n "$ENCRYPTED_KEY" | wc -c) bytes"
echo "Debug: Attempting KMS decryption..."

# Decrypt the AES key using KMS
aws kms decrypt \
    --key-id "$KMS_KEY_ARN" \
    --ciphertext-blob fileb://<(echo -n "$ENCRYPTED_KEY" | base64 -d) \
    --encryption-algorithm RSAES_OAEP_SHA_256 \
    --output text \
    --query Plaintext > /tmp/aes_key 2>/tmp/kms_error

if [ $? -ne 0 ]; then
    echo "Error: KMS decryption failed."
    echo "Debug: KMS error message:"
    cat /tmp/kms_error
    rm -f /tmp/aes_key /tmp/kms_error
    exit 1
fi

AES_KEY=$(cat /tmp/aes_key)
rm -f /tmp/aes_key /tmp/kms_error

# Decrypt the file with the AES key
echo "Decrypting file..."
openssl enc -d -aes-256-cbc -salt -in "$ENCRYPTED_FILE" \
    -out "$BASE_NAME.dec" -base64 -k "$AES_KEY" -pbkdf2

if [ $? -ne 0 ]; then
    echo "Error: File decryption failed."
    AES_KEY=""  # Clean up sensitive data
    exit 1
fi

echo "Decryption complete!"
echo "Decrypted file: ${BASE_NAME}.dec"

# Clean up variables containing sensitive data
AES_KEY=""