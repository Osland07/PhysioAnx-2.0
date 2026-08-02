import asyncio
import random

class SensorService:
    def __init__(self, page, on_data_callback):
        self.page = page
        self.on_data = on_data_callback
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.page.run_task(self._simulation_loop)

    def stop(self):
        self.is_running = False

    async def _simulation_loop(self):
        """
        Di masa depan, fungsi ini akan diganti dengan pembacaan Serial USB
        atau WebSocket langsung dari alat ESP32.
        Saat ini menggunakan generator angka untuk simulasi telemetri.
        """
        hr_val = 80.0
        gsr_val = 15.0

        while self.is_running:
            hr_val += random.randint(-4, 5)
            hr_val = max(60.0, min(130.0, hr_val))

            gsr_val += random.uniform(-1.5, 2.0)
            gsr_val = max(5.0, min(40.0, gsr_val))

            temp_val = 36.5 + random.uniform(-0.1, 0.1)

            if self.on_data:
                self.on_data(hr_val, gsr_val, temp_val)

            await asyncio.sleep(1)
