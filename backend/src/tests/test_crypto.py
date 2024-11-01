import utils.crypto as crypto
import pytest


def test_ciphertext_init():
    # Test Ciphertext constructor
    ciph_a = crypto.Ciphertext(b"a"*16, b"b"*15, b"c"*16, b"hello")
    assert type(ciph_a) == crypto.Ciphertext
    assert ciph_a.tag == b"a"*16
    assert ciph_a.nonce == b"b"*15
    assert ciph_a.salt == b"c"*16
    assert ciph_a.ciphertext == b"hello"

    # Test Ciphertext constructor passing in various non-byte values
    with pytest.raises(ValueError):
        crypto.Ciphertext("a"*16, b"b"*15, b"c"*16, b"hello")

    with pytest.raises(ValueError):
        crypto.Ciphertext(b"a"*16, 0, b"c"*16, b"hello")

    with pytest.raises(ValueError):
        crypto.Ciphertext(b"a"*16, b"b"*15, False, b"hello")

    with pytest.raises(ValueError):
        crypto.Ciphertext(b"a"*16, b"b"*15, b"c"*16, [b"hello"])


def test_ciphertext_conversion():
    # Test Ciphertext conversion to bytes
    ciph_a = crypto.Ciphertext(b"a"*16, b"b"*15, b"c"*16, b"hello")
    b = bytes(ciph_a)
    ciph_b = crypto.Ciphertext.from_bytes(b)
    assert ciph_a == ciph_b

    # Test attempting to create invalid Ciphertext
    with pytest.raises(crypto.InvalidCipherBytesException):
        crypto.Ciphertext.from_bytes(bytes(10))

    with pytest.raises(crypto.InvalidCipherBytesException):
        b = b[:-10]
        crypto.Ciphertext.from_bytes(b)

    # Ensure that Ciphertexts can be constructed out of bytes of sufficient length
    b = bytes(16+15+16)
    ciph_c = crypto.Ciphertext.from_bytes(b)
    assert type(ciph_c) == crypto.Ciphertext


def test_encrypt_decrypt():
    # Test normal encryption
    ciphertext = crypto.encrypt_str("data", "password")
    data = crypto.decrypt_str(ciphertext, "password")
    assert data == "data"

    # Test decryption where bytes are passed in
    ciphertext = bytes(ciphertext)
    data = crypto.decrypt_str(ciphertext, "password")
    assert data == "data"


def test_encrypt_decrypt_empty():
    # Test encryption with empty ciphertext
    ciphertext = crypto.encrypt_str("", "password")
    data = crypto.decrypt_str(ciphertext, "password")
    assert data == ""

    # Test encryption with empty password
    ciphertext = crypto.encrypt_str("data", "")
    data = crypto.decrypt_str(ciphertext, "")
    assert data == "data"
