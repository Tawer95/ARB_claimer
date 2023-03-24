# ARB_claimer_and_sender 

Instruction:
1. Download repo.
2. Create env and install requirements:
```
python -m pip install -r requirements. txt
```
3. Paste your private key and destination addresses in config.py
4. Paste your RPC async_claim.py
5. Run async_claim.py

0.005 eth or ~$10 for each wallet, if you need a more likely requirement, increase gasLimit and gasPrice, they can both change and affect the probability of fulfillment.
--------------------------------------------------------------------------------------

File check_eligibility.py need only for check your drop in contract. Paste your wallets in ```wallets``` like this
```
wallets = {
    1: 'YOUR ADDRESS FIRST',
    2: 'YOUR ADDRESS SECOND',
}
```
