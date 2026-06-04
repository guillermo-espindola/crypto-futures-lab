from utils.config_manager import ConfigManager
from utils.logger_interface import ILogger

class RiskEngine:
    """
    Dynamic Risk Engine
    ------------------
    Adapts position sizing and risk limits based on market regime and efficiency.
    """

    def __init__(self, config_manager: ConfigManager, logger: ILogger):
        self.config = config_manager
        self.logger = logger
        self.peak_equity = 0.0

    def calculate_position_size(
        self,
        balance: float,
        entry_price: float,
        stop_loss_price: float,
        regime_score: float = 1.0,
        efficiency_score: float = 1.0
    ) -> float:
        """
        Calculates dynamic position size based on risk per trade, stop loss,
        and market quality.
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            return 0.0

        base_risk = self.config.get("risk", "max_risk_per_trade") or 0.01

        # Risk adaptativo:
        # risk = base_risk * regime_score * efficiency_score
        # We use a baseline of 0.5 to avoid zeroing out positions in low-quality regimes
        dynamic_risk = base_risk * (0.5 + 0.5 * regime_score) * (0.7 + 0.3 * efficiency_score)

        risk_amount = balance * dynamic_risk
        stop_distance = abs(entry_price - stop_loss_price)

        if stop_distance == 0:
            return 0.0

        return risk_amount / stop_distance

    def check_risk_limits(
        self,
        balance: float,
        equity: float,
        current_exposure: float,
        leverage: float
    ) -> bool:
        """
        Validates if a trade is allowed based on dynamic risk constraints.
        """
        self.peak_equity = max(self.peak_equity, equity)

        max_dd = self.config.get("risk", "max_drawdown") or 0.15
        max_exp = self.config.get("risk", "max_total_exposure") or 0.3
        max_lev = self.config.get("risk", "max_leverage") or 10

        # 1. Drawdown Kill-switch
        if self.peak_equity > 0:
            dd = (self.peak_equity - equity) / self.peak_equity
            if dd >= max_dd:
                self.logger.warn(f"Drawdown Limit Hit: {dd:.2%}")
                return False

        # 2. Exposure Limit
        if current_exposure > (balance * max_exp):
            return False

        # 3. Leverage Limit
        if leverage > max_lev:
            return False

        return True
