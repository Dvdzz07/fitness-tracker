class NEAHasher:
    """
    Custom password hashing class for A-level NEA.
    Educational algorithm – not cryptographically secure.
    """

    def __init__(self, salt: str):
        self.salt = salt

    def hash_password(self, password: str) -> str:
        combined = self.salt + password

        h1 = 0
        h2 = 1

        for i, char in enumerate(combined):
            val = ord(char)

            # Primary accumulation
            h1 = (h1 + val * (i + 1)) % 1_000_000_007

            # Secondary mixing
            h2 = (h2 * 31 + val) % 1_000_000_009

            # Cross-mixing every few characters
            if i % 3 == 0:
                h1 ^= h2
            if i % 5 == 0:
                h2 ^= h1

        # Return as fixed-length hex string
        return f"{h1:08x}{h2:08x}"
