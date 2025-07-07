# java_random.py

class JavaRandom:
    """
    Emulates java.util.Random using a 48-bit linear congruential generator.
    Suitable for reproducing token generation based on timestamp seed.
    """
    _MULTIPLIER = 0x5DEECE66D
    _ADDEND = 0xB
    _MASK = (1 << 48) - 1

    def __init__(self, seed: int):
        if not isinstance(seed, int) or seed < 0:
            raise ValueError("Seed must be a non-negative integer.")
        # Java applies this bitmask to the seed on init
        self.seed = (seed ^ self._MULTIPLIER) & self._MASK

    def _next(self, bits: int) -> int:
        if not (0 < bits <= 32):
            raise ValueError("bits must be between 1 and 32 inclusive.")
        self.seed = (self.seed * self._MULTIPLIER + self._ADDEND) & self._MASK
        return self.seed >> (48 - bits)

    def next_int(self, bound: int) -> int:
        """
        Returns a pseudorandom, uniformly distributed int value between 0 (inclusive) and bound (exclusive).
        Follows Java's rejection-sampling approach to avoid modulo bias.
        """
        if bound <= 0:
            raise ValueError("Bound must be a positive integer.")

        if (bound & (bound - 1)) == 0:
            # Power of 2 optimization
            return (bound * self._next(31)) >> 31

        while True:
            bits = self._next(31)
            val = bits % bound
            if bits - val + (bound - 1) >= 0:
                return val