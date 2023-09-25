from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Signature import PKCS1_PSS


key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

print('private key:')
print(private_key.decode())
print('public key:')
print(public_key.decode())


data = "I met aliens in UFO. Here is the map.".encode("utf-8")

cipher_rsa = PKCS1_OAEP.new(key)


cypher = cipher_rsa.encrypt(data)

print(cypher)

clear = cipher_rsa.decrypt(cypher)


print(clear.decode())



