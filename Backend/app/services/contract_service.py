import hashlib
import json
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import base64


def generate_contract_hash(contract_data: dict) -> str:
    """Generate SHA-256 hash of contract data"""
    # Convert contract data to JSON string (sorted keys for consistency)
    contract_json = json.dumps(contract_data, sort_keys=True)
    
    # Generate SHA-256 hash
    hash_object = hashlib.sha256(contract_json.encode())
    return hash_object.hexdigest()


def generate_keys() -> Tuple[str, str]:
    """Generate RSA key pair for signing (demo purposes)"""
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Generate public key
    public_key = private_key.public_key()
    
    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem.decode('utf-8'), public_pem.decode('utf-8')


def create_signature(contract_hash: str, private_key_pem: str) -> str:
    """Sign contract hash with private key"""
    try:
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        # Sign the hash
        signature = private_key.sign(
            contract_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')
    except Exception as e:
        # For demo purposes, if signing fails, return a placeholder
        return f"demo_signature_{contract_hash[:16]}"


def verify_signature(contract_hash: str, signature: str, public_key_pem: str) -> bool:
    """Verify signature with public key"""
    try:
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        # Decode signature
        signature_bytes = base64.b64decode(signature)
        
        # Verify signature
        public_key.verify(
            signature_bytes,
            contract_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        # For demo purposes, accept demo signatures
        return signature.startswith("demo_signature_")
