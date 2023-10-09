from web3 import Web3
from config import contract_abi,contract_address
import os
from dotenv import load_dotenv
import time

# Private keyi .env sonyasından çekme
load_dotenv()
private_key = os.getenv('PRIVATE_KEY')
https_provider = os.getenv('HTTPS_PROVIDER')

# Provider kurulumu
w3 = Web3(Web3.HTTPProvider(https_provider))

# Private key ile account oluşturma
account = w3.eth.account.from_key(private_key)

# PostTech kontratı
ptContract = w3.eth.contract(address=contract_address, abi=contract_abi)
# İşlemden önce nonce çek
last_nonce = ()

# Adresi verilen hesabın komisyonlar dahil hisse fiyatını eth cinsinden float olarak verir.
def getSharePrice(adres):
    response = ptContract.caller.getBuyPriceAfterFee(w3.to_checksum_address(adres),1)
    return float(w3.from_wei(response,'ether'))

# Satın alma fonksiyonu
def buy_shares(shares_subject, amount):
    transaction = ptContract.functions.buyShares(shares_subject, amount).build_transaction({
        'chainId': 42161,  # Arbitrum 
        'gas': 400000,  # Gas limiti
        'gasPrice': w3.to_wei('0.1', 'gwei'),  # Gas fiyatını
        'nonce': last_nonce,  # Transaction nonce
        'value': w3.to_wei(0.000071875, 'ether')  # Amount miktarını wei cinsinden
    })

    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)
    transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print('İŞLEM GÖNDERİLDİ',transaction_hash.hex())


# Son bloklardan Post Tech alım satım işlemlerini bul uygun işlemde satın alma fonksiyonunu çalıştır
def getPtTx():
    r = w3.eth.get_block('latest', True)
    r = dict(r)
    txs = r.get('transactions')
    for i in txs:
        i = dict(i)
        if i['to'] == '0x87da6930626Fe0c7dB8bc15587ec0e410937e5DC':
            print('BU POST.TECH KONTRATI!!!')
            value = w3.from_wei(i['value'],'ether')
            txHash = w3.to_hex(i['hash'])
            txInput = w3.to_hex(i['input'])
            decode = ptContract.decode_function_input(txInput)
            decode = list(decode)
            action = str(decode[0])
            subAdress = dict(decode[1]).get('sharesSubject')
            amount = dict(decode[1]).get('amount')
            print(action,'\n',txHash,'\n',subAdress,'\n',amount,'\n',value)
            if action == '<Function buyShares(address,uint256)>' and value == 0:
                print('UCUZ SHARE BULUNDU')
                share_address = w3.to_checksum_address(subAdress)
                share_value = 1
                try:
                    buy_shares(share_address,share_value)
                except KeyError:
                    print('Başaramadım')
                finally:
                    continue
            else:
                pass
        else:
            pass

while True:
    last_nonce = w3.eth.get_transaction_count(account.address)
    getPtTx()
    time.sleep(0.2)
  









