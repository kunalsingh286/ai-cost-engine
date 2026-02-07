class CapacityPlanner:


    def __init__(
        self,
        tokens_per_second: int = 5000,
        vram_per_million: float = 0.8
    ):

        self.tokens_per_second = tokens_per_second
        self.vram_per_million = vram_per_million


    def estimate(self, daily_tokens: float) -> dict:

        tps_required = daily_tokens / 86400

        gpu_util = tps_required / self.tokens_per_second

        vram_needed = (
            daily_tokens / 1_000_000
        ) * self.vram_per_million

        return {
            "tokens_per_second": round(tps_required, 2),
            "gpu_utilization": round(gpu_util, 2),
            "vram_gb": round(vram_needed, 2)
        }
