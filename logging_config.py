
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("local_llm_api")


def log_request(method: str, path: str, status: int, latency: float):
    logger.info(
        "method=%s path=%s status=%s latency_ms=%.2f",
        method,
        path,
        status,
        latency * 1000,
    )
