from typing import Any, Dict, NoReturn
import psutil
import threading
import time


class StatCollector:
    def __init__(self, interval_seconds: int | float = 1) -> None:
        self._update_stats()
        self._interval = interval_seconds
        pass

    def _update_stats(self) -> None:
        self._cpu_stats = self._get_cpu_stats()
        self._memory_stats = self._get_memory_stats()

    def _get_memory_stats(self) -> Dict:
        vm = psutil.virtual_memory()
        return vm._asdict()

    def _get_cpu_stats(self) -> Dict[str, Any]:
        thread_count = psutil.cpu_count(logical=True)
        cpu_count = psutil.cpu_count(logical=False)
        overall_cpu_percent = psutil.cpu_percent(interval=0.0, percpu=False)
        percpu_cpu_percent = psutil.cpu_percent(interval=0.0, percpu=True)
        return {
            "cpu_count": cpu_count,
            "thread_count": thread_count,
            "utilization": {
                "overall": overall_cpu_percent,
                "per_cpu": percpu_cpu_percent,
            },
        }

    def get_stats(self) -> Dict[str, Any]:
        return {"cpu": self._cpu_stats, "memory": self._memory_stats}

    def run_in_thread(self) -> None:
        def threaded() -> NoReturn:
            while True:
                self._update_stats()
                time.sleep(self._interval)

        thread = threading.Thread(target=threaded, daemon=True)
        thread.start()


if __name__ == "__main__":
    from pprint import pprint

    c = StatCollector()
    c.run_in_thread()
    while True:
        pprint(c.get_stats())
        time.sleep(1)
