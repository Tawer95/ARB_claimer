import asyncio
from web3 import Web3, HTTPProvider
from ABI import claim_abi, erc20_abi
from config import prv_key_array, destination_address_array


# Connect to node
NETWORK = 'https://arb-mainnet.g.alchemy.com/v2/xxxxxxxxxxxxx' # YOUR RPC
w3 = Web3(HTTPProvider(NETWORK))

# Contract addresses
CLAIM_CONTRACT_ADDRESS = '0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9'
TOKEN_ADDRESS = '0x912CE59144191C1204E64559FE8253a0e49E6548'

checksum_dest_address = [w3.to_checksum_address(address) for address in destination_address_array]

async def send_claim_and_transfer(prv_key, dest_address):
    account = w3.eth.account.from_key(prv_key)

    # Contract instance creation
    claim_contract = w3.eth.contract(address=CLAIM_CONTRACT_ADDRESS, abi=claim_abi)
    token_contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=erc20_abi)

    # Check claimable tokens
    claimable_tokens = claim_contract.functions.claimableTokens(account.address).call()

    # Claim tokens
    txn = claim_contract.functions.claim().build_transaction(
        {
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 1000000,
            'gasPrice': w3.to_wei(0.1, 'gwei')
        }
    )
    signed_txn = account.signTransaction(txn)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Claim {claimable_tokens / 10 ** 18} txn sent for {account.address}. Txn hash: {txn_hash.hex()}")

    # Wait for the claim transaction to be mined
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    if receipt.status == 0:
        print(f"Claim txn failed for {account.address}")
        return
    # Transfer tokens to destination address
    transfer_amount = claimable_tokens
    txn = token_contract.functions.transfer(dest_address, transfer_amount).build_transaction(
        {
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 1000000,
            'gasPrice': w3.to_wei(0.1, 'gwei')
        }
    )
    signed_txn = account.signTransaction(txn)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transfer txn sent for {account.address}. Txn hash: {txn_hash.hex()}")

    # Wait for the transfer transaction to be mined
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    if receipt.status == 0:
        print(f"Transfer txn failed for {account.address}")


async def main():
    tasks = []
    for prv_key, dest_address in zip(prv_key_array, checksum_dest_address):
        tasks.append(asyncio.create_task(send_claim_and_transfer(prv_key, dest_address)))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
    print('Всё прошло успешно! Деньги отправились на ваши кошельки :)')

