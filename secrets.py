"""Utilidades simples para cifrar y descifrar texto con AES.

Uso:
	python secrets.py encrypt --phrase "mi frase secreta" --text "hola"
	python secrets.py decrypt --phrase "mi frase secreta" --text <token>

Ejemplo con variables en Python:
	phrase = "mi frase secreta"
	text_to_encrypt = "hola"
	cipher = WordCipher(phrase)
	encrypted_text = cipher.encrypt_word(text_to_encrypt)
	text_to_decrypt = encrypted_text
	decrypted_text = cipher.decrypt_word(text_to_decrypt)
"""

from __future__ import annotations

import argparse
import base64
import os
import sys

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
KDF_ITERATIONS = 390000


def derive_key(phrase: str, salt: bytes) -> bytes:
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=KEY_SIZE,
		salt=salt,
		iterations=KDF_ITERATIONS,
	)
	return kdf.derive(phrase.encode("utf-8"))


class WordCipher:
	def __init__(self, phrase: str) -> None:
		self._phrase = phrase

	def encrypt_word(self, text: str) -> str:
		salt = os.urandom(SALT_SIZE)
		nonce = os.urandom(NONCE_SIZE)
		key = derive_key(self._phrase, salt)
		cipher = AESGCM(key)
		ciphertext = cipher.encrypt(nonce, text.encode("utf-8"), None)
		token = salt + nonce + ciphertext
		return base64.urlsafe_b64encode(token).decode("utf-8")

	def decrypt_word(self, token: str) -> str:
		try:
			decoded = base64.urlsafe_b64decode(token.encode("utf-8"))
			salt = decoded[:SALT_SIZE]
			nonce = decoded[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
			ciphertext = decoded[SALT_SIZE + NONCE_SIZE:]
			key = derive_key(self._phrase, salt)
			cipher = AESGCM(key)
			decrypted = cipher.decrypt(nonce, ciphertext, None)
		except (InvalidTag, ValueError) as error:
			raise ValueError("El texto cifrado o la phrase no son validos.") from error
		return decrypted.decode("utf-8")


def encrypt_text(phrase: str, text: str) -> str:
	return WordCipher(phrase).encrypt_word(text)


def decrypt_text(phrase: str, token: str) -> str:
	return WordCipher(phrase).decrypt_word(token)


def example_usage() -> None:
	# Cambia estas variables por tus propios valores.
	phrase = "mi_frase_secreta"
	text_to_encrypt = "TEXTO_CIFRAR"
	encrypted_text = encrypt_text(phrase, text_to_encrypt)
	print(f"Texto cifrado: {encrypted_text}")

	text_to_decrypt = "TEXTO_DESCIFRAR"
	decrypted_text = decrypt_text(phrase, text_to_decrypt)
	print(f"Texto descifrado: {decrypted_text}")


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Cifra y descifra palabras con AES-GCM.")
	subparsers = parser.add_subparsers(dest="command", required=True)

	encrypt_parser = subparsers.add_parser("encrypt", help="Cifra un texto.")
	encrypt_parser.add_argument("--phrase", required=True, help="Frase secreta usada para derivar la clave AES.")
	encrypt_parser.add_argument("--text", required=True, help="Texto a cifrar.")

	decrypt_parser = subparsers.add_parser("decrypt", help="Descifra un texto.")
	decrypt_parser.add_argument("--phrase", required=True, help="Frase secreta usada al cifrar.")
	decrypt_parser.add_argument("--text", required=True, help="Texto cifrado a descifrar.")

	return parser


def main() -> None:
	if len(sys.argv) == 1:
		example_usage()
		return

	parser = build_parser()
	args = parser.parse_args()
	cipher = WordCipher(args.phrase)

	if args.command == "encrypt":
		print(cipher.encrypt_word(args.text))
		return

	if args.command == "decrypt":
		print(cipher.decrypt_word(args.text))
		return

	parser.error("Comando no soportado.")


if __name__ == "__main__":
	main()