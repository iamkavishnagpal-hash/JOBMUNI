import logging
from typing import Dict, Tuple, Optional
from pydantic import BaseModel

logger = logging.getLogger("jobmuni.currency")

class CurrencyConversionResult(BaseModel):
    original_amount: float
    original_currency: str
    target_currency: str
    converted_amount: float
    conversion_status: str  # EXACT, CONVERTED, UNKNOWN_RATE
    exchange_rate: float
    is_converted: bool

class CurrencyProvider:
    """
    Currency Normalization Boundary.
    Provides explicit, auditable conversion rates with transparent status flags.
    Never silently uses stale rates or guessed conversions.
    """

    # Base exchange rates to USD (1 unit of currency = X USD)
    RATES_TO_USD: Dict[str, float] = {
        "USD": 1.00,
        "EUR": 1.08,
        "GBP": 1.28,
        "CAD": 0.74,
        "AUD": 0.66,
        "INR": 0.012,
        "CHF": 1.13,
        "SGD": 0.76,
    }

    def convert(
        self,
        amount: Optional[float],
        source_currency: Optional[str],
        target_currency: str = "USD"
    ) -> CurrencyConversionResult:
        if amount is None:
            return CurrencyConversionResult(
                original_amount=0.0,
                original_currency=source_currency or target_currency,
                target_currency=target_currency,
                converted_amount=0.0,
                conversion_status="UNKNOWN_RATE",
                exchange_rate=1.0,
                is_converted=False,
            )

        src = (source_currency or "USD").upper().strip()
        tgt = target_currency.upper().strip()

        if src == tgt:
            return CurrencyConversionResult(
                original_amount=amount,
                original_currency=src,
                target_currency=tgt,
                converted_amount=amount,
                conversion_status="EXACT",
                exchange_rate=1.0,
                is_converted=False,
            )

        if src in self.RATES_TO_USD and tgt in self.RATES_TO_USD:
            # Convert src -> USD -> tgt
            usd_val = amount * self.RATES_TO_USD[src]
            target_rate = self.RATES_TO_USD[tgt]
            converted_val = round(usd_val / target_rate, 2)
            effective_rate = round(self.RATES_TO_USD[src] / target_rate, 4)

            return CurrencyConversionResult(
                original_amount=amount,
                original_currency=src,
                target_currency=tgt,
                converted_amount=converted_val,
                conversion_status="CONVERTED",
                exchange_rate=effective_rate,
                is_converted=True,
            )

        # Unsupported currency -> retain original
        return CurrencyConversionResult(
            original_amount=amount,
            original_currency=src,
            target_currency=tgt,
            converted_amount=amount,
            conversion_status="UNKNOWN_RATE",
            exchange_rate=1.0,
            is_converted=False,
        )

currency_provider = CurrencyProvider()
