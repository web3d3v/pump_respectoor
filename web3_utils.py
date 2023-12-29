import decimal
from web3 import Web3, AsyncWeb3

MIN_WEI = 0
MAX_WEI = 2 ** 256 - 1

units = {
    '1': decimal.Decimal('1'),  # noqa: E241
    '2': decimal.Decimal('1000'),  # noqa: E241
    '3': decimal.Decimal('1000'),  # noqa: E241
    '4': decimal.Decimal('1000'),  # noqa: E241
    '5': decimal.Decimal('1000000'),  # noqa: E241
    '6': decimal.Decimal('1000000'),  # noqa: E241
    '7': decimal.Decimal('1000000'),  # noqa: E241
    '8': decimal.Decimal('1000000000'),  # noqa: E241
    '9': decimal.Decimal('1000000000'),  # noqa: E241
    '10': decimal.Decimal('1000000000'),  # noqa: E241
    '11': decimal.Decimal('1000000000'),  # noqa: E241
    '12': decimal.Decimal('1000000000000'),  # noqa: E241
    '13': decimal.Decimal('1000000000000'),  # noqa: E241
    '14': decimal.Decimal('1000000000000'),  # noqa: E241
    '15': decimal.Decimal('1000000000000000'),  # noqa: E241
    '16': decimal.Decimal('1000000000000000'),  # noqa: E241
    '17': decimal.Decimal('1000000000000000'),  # noqa: E241
    '18': decimal.Decimal('1000000000000000000'),  # noqa: E241
    '19': decimal.Decimal('1000000000000000000000'),  # noqa: E241
    '20': decimal.Decimal('1000000000000000000000'),  # noqa: E241
    '21': decimal.Decimal('1000000000000000000000000'),  # noqa: E241
    '22': decimal.Decimal('1000000000000000000000000000'),  # noqa: E241
    '23': decimal.Decimal('1000000000000000000000000000000'),  # noqa: E241
}


def format_decimals(number: int, decimals: str) -> decimal.Decimal:
    if number == 0:
        return 0

    if number < MIN_WEI or number > MAX_WEI:
        raise ValueError("value must be between 1 and 2**256 - 1")

    unit_value = units.get(str(decimals))

    if unit_value is None:
        raise ValueError("Unsupported decimals", decimals)

    with decimal.localcontext() as ctx:
        ctx.prec = 999
        d_number = decimal.Decimal(value=number, context=ctx)
        result_value = d_number / unit_value

    return result_value


import arrow


def get_block_near(timestamp: int, provider: Web3) -> int:
    latest_block_number = provider.eth.get_block('latest')['number']

    def iblock_near(
            tunix_s,
            left_block_tuple,
            right_block_tuple,
            provider,
    ):
        left_block = left_block_tuple[0]
        right_block = right_block_tuple[0]
        left_timestamp = left_block_tuple[1]
        right_timestamp = right_block_tuple[1]

        if left_block == right_block:
            return left_block
        # Return the closer one, if we're already between blocks
        if left_block == right_block - 1 or tunix_s <= left_timestamp or tunix_s >= right_timestamp:
            return left_block if abs(tunix_s - left_block_tuple[1]) < abs(tunix_s - right_block_tuple[1]) else right_block

        # K is how far inbetween left and right we're expected to be
        k = (tunix_s - left_timestamp) / (right_timestamp - left_timestamp)
        # We bound, to ensure logarithmic time even when guesses aren't great
        k = min(max(k, 0.05), 0.95)
        # We get the expected block number from K
        expected_block = round(left_block + k * (right_block - left_block))
        # Make sure to make some progress
        expected_block = min(max(expected_block, left_block + 1), right_block - 1)

        # Get the actual timestamp for that block
        expected_block_timestamp = provider.eth.get_block(expected_block).timestamp

        # Adjust bound using our estimated block
        if expected_block_timestamp < tunix_s:
            left_block = expected_block
            left_timestamp = expected_block_timestamp
        elif expected_block_timestamp > tunix_s:
            right_block = expected_block
            right_timestamp = expected_block_timestamp
        else:
            # Return the perfect match
            return expected_block

        # Recurse using tightened bounds
        return iblock_near(tunix_s, (left_block, left_timestamp), (right_block, right_timestamp), provider)

    return iblock_near(
        timestamp,
        (1, provider.eth.get_block(1).timestamp),
        (latest_block_number, provider.eth.get_block('latest').timestamp),
        provider,
    )
