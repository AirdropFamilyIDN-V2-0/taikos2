import time
import json
from web3 import Web3
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Inisialisasi colorama
init(autoreset=True)

banner = """
===================================
|       AUTO TX TAIKO BOT         |
| @AirdropFamilyIDN X @ylasgamers |
===================================
"""
print(Fore.CYAN + banner)

# Membaca dan menghitung jumlah kunci pribadi
with open('pvkeylist.txt', 'r') as file:
    pvkeylist = file.read().splitlines()
    num_keys = len(pvkeylist)

print(Fore.CYAN + f"Jumlah Akun : {num_keys}\n")

# Daftar RPC
rpc_list = [
    "https://rpc.ankr.com/taiko",
    "https://taiko-rpc.publicnode.com",
    "https://taiko.drpc.org",
    "https://rpc.taiko.xyz",
    "https://taiko-json-rpc.stakely.io",
    "https://rpc.mainnet.taiko.xyz",
    "https://taiko-mainnet.rpc.porters.xyz/taiko-public"
]

# Fungsi untuk menghubungkan ke RPC
def connect_to_rpc():
    for rpc_url in rpc_list:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        if web3.is_connected():
            print(Fore.GREEN + f"Web3 Connected to RPC: {rpc_url}\n")
            return web3
        else:
            print(Fore.RED + f"Failed to connect to RPC: {rpc_url}")
    print(Fore.RED + "Error Connecting to all RPCs. Exiting...")
    exit()

# Menghubungkan ke RPC
web3 = connect_to_rpc()
chainId = web3.eth.chain_id

# Input manual untuk jeda waktu antar transaksi dalam menit
delay_minutes = int(input("Input jeda transaksi dalam menit : "))
delay_seconds = delay_minutes * 60

# Input jumlah transaksi yang diinginkan
num_transactions = int(input("Input jumlah transaksi : "))

# Menghitung jumlah transaksi yang telah dilakukan
transactions_done = 0
successful_transactions = {}

voteaddr = web3.to_checksum_address("0x4D1E2145082d0AB0fDa4a973dC4887C7295e21aB")
voteabi = json.loads('[{"stateMutability":"payable","type":"fallback"},{"inputs":[],"name":"vote","outputs":[],"stateMutability":"payable","type":"function"}]')
vote_contract = web3.eth.contract(address=voteaddr, abi=voteabi)

def vote(wallet, key):
    global transactions_done
    try:
        nonce = web3.eth.get_transaction_count(wallet)
        gasAmount = vote_contract.functions.vote().estimate_gas({
            'chainId': chainId,
            'from': wallet
        })
        gasPrice = 5050/gasAmount
        votetx = vote_contract.functions.vote().build_transaction({
            'chainId': chainId,
            'from': wallet,
            'gas': gasAmount,
            'maxFeePerGas': web3.to_wei(gasPrice, 'gwei'),
            'maxPriorityFeePerGas': web3.to_wei(gasPrice, 'gwei'),
            'nonce': nonce
        })
        #sign & send the transaction
        print(Fore.GREEN + f'Processing Vote For Wallet Address {wallet}')
        tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(votetx, key).rawTransaction)
        print(Fore.GREEN + f'Processing Vote Success!')
        print(f'TX-ID : {str(web3.to_hex(tx_hash))}')
        print(Fore.GREEN + f'Transaksi berhasil untuk alamat: {wallet}')


        for remaining in range(delay_seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            timeformat = '{:02d}:{:02d}'.format(int(mins), int(secs))
            print(Fore.YELLOW + f"Waiting for next transaction: {timeformat}", end='\r')
            time.sleep(1)
        print('\n')

        transactions_done += 1

        if wallet not in successful_transactions:
            successful_transactions[wallet] = 0
        successful_transactions[wallet] += 1
        print(Fore.CYAN + f'Jumlah transaksi berhasil untuk {wallet}: {successful_transactions[wallet]}')

    except Exception as e:
        print(Fore.RED + f'Error: {e}')
        print(Fore.YELLOW + f'Transaksi gagal untuk alamat: {wallet}. Akan mencoba lagi...')
        vote(wallet, key)
        pass


while transactions_done < num_transactions:
    with open('pvkeylist.txt', 'r') as file:
        pvkeylist = file.read().splitlines()
        for loadkey in pvkeylist:
            if transactions_done >= num_transactions:
                print(Fore.GREEN + f"Tugas selesai {transactions_done} transaksi.")
                exit()
            wallet = web3.eth.account.from_key(loadkey)
            vote(wallet.address, wallet.key)
