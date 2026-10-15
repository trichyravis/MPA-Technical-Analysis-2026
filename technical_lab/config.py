from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Settings:
    short_ma: int = 20
    fast_ma: int = 50
    slow_ma: int = 200
    sr_period: int = 20
    sr_basis: str = "High/Low"
    roc_period: int = 12
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    swing_window: int = 3

    def validate(self):
        for key, value in asdict(self).items():
            if key != "sr_basis" and (not isinstance(value, int) or not 1 <= value <= 500):
                raise ValueError(f"{key} must be an integer from 1 to 500.")
        if not self.short_ma < self.fast_ma < self.slow_ma:
            raise ValueError("MA periods must satisfy short < fast < slow.")
        if self.macd_fast >= self.macd_slow:
            raise ValueError("MACD fast period must be below the slow period.")
        if self.rsi_period < 2 or self.macd_signal < 2:
            raise ValueError("RSI and MACD signal periods must be at least 2.")
        if self.sr_basis not in {"High/Low", "Close"}:
            raise ValueError("Unknown support/resistance basis.")
        return self
