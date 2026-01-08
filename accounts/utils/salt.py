class NEASaltGenerator:
  

    def __init__(self, seed_text: str):
        self.seed_text = seed_text

    def generate(self) -> str:
        # Convert the seed text into numbers and mix them
        s1 = 0
        s2 = 1

        for i, ch in enumerate(self.seed_text):
            v = ord(ch)

            s1 = (s1 + v * (i + 7)) % 1_000_000_007
            s2 = (s2 * 33 + v) % 1_000_000_009

            if i % 4 == 0:
                s1 ^= s2
            if i % 6 == 0:
                s2 ^= s1

        # 32 hex characters total (good length for storing)
        return f"{s1:08x}{s2:08x}{(s1 ^ s2):08x}{(s1 + s2) % (2**32):08x}"
