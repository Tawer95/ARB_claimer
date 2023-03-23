import asyncio
from web3 import Web3, HTTPProvider
from ABI import claim_abi, erc20_abi
from config import prv_key_array, destination_address_array


# Connect to node
NETWORK = 'https://arbitrum-one.public.blastapi.io' # OR YOUR OWN RPC!!!
w3 = Web3(HTTPProvider(NETWORK))

# Contract addresses
CLAIM_CONTRACT_ADDRESS = '0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9'
TOKEN_ADDRESS = '0x912CE59144191C1204E64559FE8253a0e49E6548'


async def send_claim_and_transfer(prv_key, dest_address):
    account = w3.eth.account.from_key(prv_key)

    # Contract instance creation
    claim_contract = w3.eth.contract(address=CLAIM_CONTRACT_ADDRESS, abi=claim_abi)
    token_contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=erc20_abi)

    # Check claimable tokens
    claimable_tokens = claim_contract.functions.claimableTokens(account.address).call()

    # Claim tokens
    txn = claim_contract.functions.claim().buildTransaction(
        {
            'from': account.address,
            'nonce': w3.eth.getTransactionCount(account.address),
            'gas': 300000,
            'gasPrice': w3.toWei(1, 'gwei')
        }
    )
    signed_txn = account.signTransaction(txn)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Claim {claimable_tokens / 10 ** 18} txn sent for {account.address}. Txn hash: {txn_hash.hex()}")

    # Wait for the claim transaction to be mined
    receipt = w3.eth.waitForTransactionReceipt(txn_hash)
    if receipt.status == 0:
        print(f"Claim txn failed for {account.address}")
        return

    # Transfer tokens to destination address
    transfer_amount = claimable_tokens
    txn = token_contract.functions.transfer(dest_address, transfer_amount).buildTransaction(
        {
            'from': account.address,
            'nonce': w3.eth.getTransactionCount(account.address),
            'gas': 300000,
            'gasPrice': w3.toWei(1, 'gwei')
        }
    )
    signed_txn = account.signTransaction(txn)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Transfer txn sent for {account.address}. Txn hash: {txn_hash.hex()}")

    # Wait for the transfer transaction to be mined
    receipt = w3.eth.waitForTransactionReceipt(txn_hash)
    if receipt.status == 0:
        print(f"Transfer txn failed for {account.address}")


async def main():
    tasks = []
    for prv_key, dest_address in zip(prv_key_array, destination_address_array):
        tasks.append(asyncio.create_task(send_claim_and_transfer(prv_key, dest_address)))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
