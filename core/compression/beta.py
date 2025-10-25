from math import log


def compress(value: bytes, chunk_size: int = 256, precision: int = 16):
    print(f"@-> Compressing {len(value)} bytes")
    int_logs: list[int] = []
    for chunk in range(0, len(value), chunk_size):
        chunk_data: int = int.from_bytes(value[chunk : chunk + chunk_size], "big")
        base: int = max(2, chunk_data.bit_length() // (chunk_size * 2))
        logs: list[float] = []
        signs: list[int] = []
        remainder = chunk_data
        while True:
            log_exponent = log(remainder, base)
            remainder = remainder - 2**log_exponent
            if remainder < 0:
                signs.append(len(logs))
            remainder = abs(remainder)
            logs.append(log_exponent)
            if remainder == 0:
                break
        for flog in logs:
            int_logs.append(int(flog * 10**precision))
        print(signs)
    print(int_logs)
    print(f"{sum([x.bit_length() for x in int_logs])/8} bytes")
