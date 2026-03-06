# certs.py
from __future__ import annotations  # postpone annotation evaluation; prevents NameError at import time
from pathlib import Path
import ssl
import ipaddress
import datetime

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

CERT_DIR = Path(".certs")
CERT_FILE = CERT_DIR / "localhost.pem"
KEY_FILE = CERT_DIR / "localhost-key.pem"

def ensure_dev_cert(days_valid: int = 365 * 2) -> tuple[ssl.SSLContext, Path, Path]:
    """
    Create a self-signed 'localhost' cert if needed, then return an SSLContext and paths.
    """
    CERT_DIR.mkdir(parents=True, exist_ok=True)

    if not (CERT_FILE.exists() and KEY_FILE.exists()):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Dev Local"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        now = datetime.datetime.utcnow()
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=5))
            .not_valid_after(now + datetime.timedelta(days=days_valid))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    x509.IPAddress(ipaddress.IPv6Address("::1")),
                ]),
                critical=False,
            )
            .add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False,
            )
            .sign(private_key=key, algorithm=hashes.SHA256())
        )

        with KEY_FILE.open("wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))
        with CERT_FILE.open("wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(certfile=str(CERT_FILE), keyfile=str(KEY_FILE))
    try:
        ctx.set_alpn_protocols(["h2", "http/1.1"])
    except NotImplementedError:
        pass
    return ctx, CERT_FILE, KEY_FILE
