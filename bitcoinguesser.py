import secrets
import base58
import hashlib
import sys
import requests
import time

import binascii

from bitcoinaddress import Wallet


#=========taken from stackoverflow lol===============================
# alias method
decode_hex = binascii.unhexlify

# wallet import format key - base58 encoded format
def gen_wif_key(private_key):
    # prepended mainnet version byte to private key
    mainnet_private_key = '80' + private_key

    # perform SHA-256 hash on the mainnet_private_key
    sha256 = hashlib.sha256()
    sha256.update( decode_hex(mainnet_private_key) )
    hash = sha256.hexdigest()

    # perform SHA-256 on the previous SHA-256 hash
    sha256 = hashlib.sha256()
    sha256.update( decode_hex(hash) )
    hash = sha256.hexdigest()

    # create a checksum using the first 4 bytes of the previous SHA-256 hash
    # append the 4 checksum bytes to the mainnet_private_key
    checksum = hash[:8]
    hash = mainnet_private_key + checksum

    # convert mainnet_private_key + checksum into base58 encoded string
    return base58.b58encode( decode_hex(hash) )
#=========taken from stackoverflow lol===============================

def genwalletinfo():
    privguess = secrets.token_hex(32)

    wif = gen_wif_key(privguess)
    wif = str(wif.decode('UTF-8'))

    wallet = Wallet(wif)
    info = wallet.address.__dict__['mainnet'].__dict__
    legacy = info['pubaddr1']
    bch = info['pubaddrbc1_P2WPKH']

    wall = dict()

    wall['privguess'] = privguess
    wall['wif'] = wif
    wall['legacy'] = legacy
    wall['bch'] = bch

    return wall


def main():
    guessCounter = 0

    while True :

        walllist = list()
        for x in range(0, 50):
            walllist.append(genwalletinfo())

        urlpath = ""
        for wallet in walllist:
            urlpath = urlpath +  wallet['legacy'] + "|" + wallet['bch'] + "|"

        URL = "https://blockchain.info/multiaddr?active="+ urlpath;
        
        # URL = 'https://blockchain.info/multiaddr?active=bc1qdaw0z2hn6rlqthxmsjyj4cqsmtfdmzg6kq8re2|18EUPpv14cKuDWyAwodss7zMYq8BzJw5bT|bc1qq3hnrglt54qveq7zf53kcrk3qh9ren8eq0vjgk'
        #print(URL)

        r = requests.get(url = URL)

        data = r.json()
        for address in data['addresses']:
            if address['final_balance'] > 0:
                for wallet in walllist:
                    if address['address'] == wallet['legacy'] or address['address'] == wallet['bch']:

                        print("FOUND ACTIVE ADDRESS: " + address['address'])
                        print("LEGACY WALLET ADDR: " + wallet['legacy'])
                        print("BCH WALLET ADDR: " + wallet['bch'])
                        print("PRIVATE KEY: "+ wallet['privguess'])
                        print("WIF: " + wallet['wif'])
                        print("URL: " + URL)
                        print()

        guessCounter += len(walllist)*2

        print("[] Guesses: " + str(guessCounter), end='\r')
        time.sleep(3)
        
if __name__ == '__main__':
    print("--Running BTC wallet Guesser v1.0--")
    main()
