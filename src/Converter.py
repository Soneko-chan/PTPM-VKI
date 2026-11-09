class Converter:
    @staticmethod
    def do(x: float) -> int:
        if x >= 100.7:
            return 1000
        if x > 0:
            return int(x)
        if x == 0.0:
            raise ValueError("x cannot be 0.0")
        if x >= -30.4:          # здесь уже известно, что x < 0
            return int(x) - 5
        # осталось x <= -30.5
        return -2000