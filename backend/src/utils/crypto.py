from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import sys

# Import Self from the correct place depending on the Python version
if sys.version_info[0] == 3 and sys.version_info[1] >= 11:
    from typing import Self
else:
    from typing_extensions import Self

class Ciphertext:
    """
    A representation of AES-OCB (256 bit) encrypted ciphertext. Can be converted to and from bytes.
    """
    def __init__(self, tag: bytes, nonce: bytes, salt: bytes, ciphertext: bytes) -> Self:
        """
        Initialize a Ciphertext.

        :param tag: The tag for the ciphertext.
        :param nonce: The nonce used to encrypt the ciphertext.
        :param salt: The salt used to derive the encryption key.
        :param ciphertext: The ciphertext itself.
        :raises ValueError: If any argument is not bytes.
        """
        if type(tag) != bytes or \
           type(nonce) != bytes or \
           type(salt) != bytes or \
           type(ciphertext) != bytes:
        
            raise ValueError()

        self.tag = tag
        self.nonce = nonce
        self.salt = salt
        self.ciphertext = ciphertext


    def to_bytes(self) -> bytes:
        """
        Convert Ciphertext to bytes. This is an alias for calling bytes(obj).
        """
        return bytes(self)
    

    def __bytes__(self):
        return self.tag + self.nonce + self.salt + self.ciphertext


    def __eq__(self, other):
        if type(other) != Ciphertext:
            return False

        return self.tag == other.tag and \
               self.nonce == other.nonce and \
               self.salt == other.salt and \
               self.ciphertext == other.ciphertext


    @staticmethod
    def from_bytes(data: bytes) -> Self:
        """
        Convert bytes to a Ciphertext.

        :param data: The bytes to convert into a Ciphertext.
        :return Self: The Ciphertext created from the bytes.
        :raises InvalidCipherBytesException: If the bytes clearly do not represent a Ciphertext.
        """
        # If there are less than 47 bytes, the bytes can't possibly be ciphertext
        # 16 bytes for the tag, 15 bytes for the nonce, 16 bytes for the salt
        if len(data) < 16 + 15 + 16:
            raise InvalidCipherBytesException()

        tag = data[:16]                 # First 16 bytes are the tag
        nonce = data[16:16+15]          # Next 15 bytes are the nonce
        salt = data[16+15:16+15+16]     # Next 16 bytes are the salt
        ciphertext = data[16+15+16:]    # Everything else is the ciphertext

        return Ciphertext(tag, nonce, salt, ciphertext)


class InvalidCipherBytesException(Exception):
    """
    Indicates that the bytes that were used to create a Ciphertext could not possibly represent a
    valid Ciphertext.
    """
    pass


def encrypt_str(data: str, password: str) -> Ciphertext:
    """
    Encrypt some data with the specified password using 256-bit AES-OCB.

    :param data: The date to encrypt.
    :param password: The password to encrypt the data with.
    :return Ciphertext: The encrypted data as a Ciphertext.
    """
    # Generate a key from the password
    key, salt = _derive_key(password)

    # Encrypt the data
    cipher = AES.new(key, AES.MODE_OCB)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())

    return Ciphertext(tag, cipher.nonce, salt, ciphertext)


def decrypt_str(ciphertext: Ciphertext|bytes, password: str) -> str:
    """
    Decrypt some data with the specified password using 256-bit AES-OCB.

    :param ciphertext: Either a Ciphertext object or bytes respresenting a Ciphertext object.
    :param password: The password to decrypt the data with.
    :return str: The decrypted data.
    :raises InvalidCipherBytesException: If ciphertext is bytes and clearly does not represent a
    Ciphertext.
    :raises ValueError: If the given password is incorrect or the ciphertext has been modified.
    """
    if type(ciphertext) == bytes:
        ciphertext = Ciphertext.from_bytes(ciphertext)

    # Generate a key from the password and salt
    key, salt = _derive_key(password, ciphertext.salt)

    # Decrypt the data
    cipher = AES.new(key, AES.MODE_OCB, nonce=ciphertext.nonce)
    data = cipher.decrypt_and_verify(ciphertext.ciphertext, ciphertext.tag)

    return data.decode()


def reencrypt_str(ciphertext: Ciphertext|bytes, old_password: str, new_password: str) -> Ciphertext:
    """
    Decrypt some data, then re-encrypted it with a new password.

    :param ciphertext: The Ciphertext or bytes to re-encrypt.
    :param old_password: The password that will currently decrypt the data.
    :param new_password: The password that the data will be re-encrypted with.
    :raises InvalidCipherBytesException: If ciphertext is bytes and clearly does not represent a
    Ciphertext.
    :raises ValueError: If the given password is incorrect or the ciphertext has been modified.
    """
    data = decrypt_str(ciphertext, old_password)
    return encrypt_str(data, new_password)


def generate_key() -> bytes:
    """
    Generates a random encryption key for 256-bit AES-OCB encryption.

    :return bytes: The generated key.
    """
    return get_random_bytes(32)


def _derive_key(password: str, salt: str|None=None) -> tuple[bytes, bytes]:
    """
    Derive a key from a password to encrypt some data.

    :param password: The password to derive the key from.
    :param salt: If specified, the salt used to derive the key. If None, a 16 byte salt is randomly
    generated.
    :return tuple[bytes, bytes]: The derived key as bytes and the salt used to derive it.
    """
    if salt == None:
        salt = get_random_bytes(16)
    
    # Values for scrypt chosen from:
    # https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#scrypt
    return (scrypt(password, salt, 32, N=2**17, r=8, p=1), salt)

