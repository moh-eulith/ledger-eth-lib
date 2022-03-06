"""
Test higher level transaction functionality
"""
from eth_utils import decode_hex
from ledgereth.objects import Transaction
from ledgereth.transactions import create_transaction, sign_transaction


def test_pre_155_send(yield_dongle):
    """Test sending a transaction without EIP-155 (old style), without a chain
    ID"""
    with yield_dongle() as dongle:
        # One can also use create_transaction(), this is ust to add some coverage
        tx = Transaction(
            destination=decode_hex(
                "0xf0155486a14539f784739be1c02e93f28eb8e960"
            ),
            amount=int(1e17),
            gas_limit=int(1e6),
            gas_price=int(1e9),
            data=b"",
            nonce=0,
        )
        signed = sign_transaction(tx, dongle=dongle)

        assert signed.v in (37, 38)
        assert signed.r
        assert signed.s


def test_mainnet_send(yield_dongle):
    """Test a mainnet transaction"""
    CHAIN_ID = 1

    with yield_dongle() as dongle:
        signed = create_transaction(
            destination="0xf0155486a14539f784739be1c02e93f28eb8e960",
            amount=int(1e17),
            gas=int(1e6),
            gas_price=int(1e9),
            data="",
            nonce=0,
            chain_id=CHAIN_ID,
            dongle=dongle,
        )

        assert signed.v in [(CHAIN_ID * 2 + 35) + x for x in (0, 1)]
        assert signed.r
        assert signed.s


def test_rinkeby_send(yield_dongle):
    """Test a rinkeby transaction"""
    CHAIN_ID = 4

    with yield_dongle() as dongle:
        signed = create_transaction(
            destination="0xf0155486a14539f784739be1c02e93f28eb8e960",
            amount=int(1e17),
            gas=int(1e6),
            gas_price=int(1e9),
            data="",
            nonce=0,
            chain_id=CHAIN_ID,
            dongle=dongle,
        )

        assert signed.v in [(CHAIN_ID * 2 + 35) + x for x in (0, 1)]
        assert signed.r
        assert signed.s


def test_eip2930_send(yield_dongle):
    """Test a type 1 (EIP-2930) transaction"""
    CHAIN_ID = 3
    address = "0xb2bb2b958afa2e96dab3f3ce7162b87daea39017"
    gas_price = int(1e9)

    with yield_dongle() as dongle:
        # Matches tx from app-ethereum tests
        signed = create_transaction(
            destination=address,
            amount=int(1e16),  # 0.01 ETH
            gas=21000,
            gas_price=gas_price,
            data="",
            nonce=42,
            chain_id=CHAIN_ID,
            access_list=[(address, [1, 2, 3])],
            dongle=dongle,
        )

        assert signed.gas_price == gas_price
        # Transactions after EIP-2930 use a parity byte instead of "v"
        assert signed.y_parity in (0, 1)
        assert signed.sender_r
        assert signed.sender_s


def test_eip1559_send(yield_dongle):
    """Test a type 2 (EIP-1559) transaction"""
    CHAIN_ID = 3
    max_priority_fee_per_gas = int(1e9)
    max_fee_per_gas = int(20e9)

    with yield_dongle() as dongle:
        # Matches tx from app-ethereum tests
        signed = create_transaction(
            destination="0xb2bb2b958afa2e96dab3f3ce7162b87daea39017",
            amount=int(1e16),  # 0.01 ETH
            gas=21000,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            max_fee_per_gas=max_fee_per_gas,
            data="",
            nonce=6,
            chain_id=CHAIN_ID,
            dongle=dongle,
        )

        assert signed.max_priority_fee_per_gas == max_priority_fee_per_gas
        assert signed.max_fee_per_gas == max_fee_per_gas
        # Transactions after EIP-2930 use a parity byte instead of "v"
        assert signed.y_parity in (0, 1)
        assert signed.sender_r
        assert signed.sender_s