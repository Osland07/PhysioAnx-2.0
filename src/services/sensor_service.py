import asyncio
import re
from services.ble_receiver import BLEReceiver

class SensorService:
    _instance = None

    @classmethod
    def get_instance(cls, page=None):
        if cls._instance is None:
            cls._instance = SensorService(page)
            cls._instance.start()
        elif page is not None:
            cls._instance.page = page
        return cls._instance

    def __init__(self, page=None):
        self.page = page
        self.on_data = None
        self.on_status = None
        self.on_prediction = None
        self.is_running = False
        self.ble_receiver = None
        self.connection_state = "disconnected"  # "connected", "searching", "disconnected"
        self.last_status_detail = "Belum Terhubung"

        # Buffer & cached state for fragmented telemetry chunks over BLE
        self.current_hr = 0.0
        self.current_temp = 36.5
        self.current_gsr = 0.0
        self.has_received_hr = False
        self.has_received_gsr = False

    def register_callbacks(self, on_data=None, on_status=None, on_prediction=None):
        self.on_data = on_data
        self.on_status = on_status
        self.on_prediction = on_prediction

        # Langsung kirim status koneksi saat ini ke halaman yang baru dibuka
        if self.on_status:
            self._safe_callback(self.on_status, "connection", self.connection_state, self.last_status_detail)

    def start(self):
        if self.is_running:
            return

        self.is_running = True
        self._start_ble()

    def stop(self):
        self.is_running = False
        if self.ble_receiver:
            self.ble_receiver.stop()
            self.ble_receiver = None

    def _start_ble(self):
        if self.ble_receiver is None:
            self.ble_receiver = BLEReceiver(
                callback_func=self._handle_ble_message,
                status_callback=self._handle_ble_status
            )
            self.ble_receiver.start_background()

    def _handle_ble_status(self, status: str, detail: str):
        self.connection_state = status
        self.last_status_detail = detail
        if self.on_status:
            self._safe_callback(self.on_status, "connection", status, detail)

    def _handle_ble_message(self, message: str):
        if not self.is_running:
            return

        msg_clean = message.strip()

        # 1. Parse Telemetry data (supports single-line, shorthand H:83|T:34.4|G:0.91, and split BLE MTU chunks)
        hr_match = re.search(r'(?:HR|H):\s*([\d.]+)', msg_clean, re.IGNORECASE)
        temp_match = re.search(r'(?:Suhu|Temp|T):\s*([\d.]+)', msg_clean, re.IGNORECASE)
        gsr_match = re.search(r'(?:GSR|G):\s*([\d.]+)', msg_clean, re.IGNORECASE)

        data_updated = False
        if hr_match:
            try:
                self.current_hr = float(hr_match.group(1))
                self.has_received_hr = True
                data_updated = True
            except Exception as e:
                print(f"[SensorService] Error parsing HR: {e}")

        if temp_match:
            try:
                self.current_temp = float(temp_match.group(1))
                data_updated = True
            except Exception as e:
                print(f"[SensorService] Error parsing Temp: {e}")

        if gsr_match:
            try:
                self.current_gsr = float(gsr_match.group(1))
                self.has_received_gsr = True
                data_updated = True
            except Exception as e:
                print(f"[SensorService] Error parsing GSR: {e}")

        # Trigger telemetry data callback when a frame completes (on GSR match or full single line)
        if data_updated and self.has_received_hr and self.has_received_gsr:
            if gsr_match or (hr_match and temp_match and gsr_match):
                if self.on_data:
                    self._safe_callback(self.on_data, self.current_hr, self.current_gsr, self.current_temp)

        # 2. Parse Scan Start status
        if re.search(r'(?:Scanning|Tombol|Start)', msg_clean, re.IGNORECASE):
            if self.on_status:
                self._safe_callback(self.on_status, "scan_status", "scanning", "Pengukuran sedang berlangsung...")

        # 3. Parse Scan Finish status
        if re.search(r'(?:Finish|Selesai)', msg_clean, re.IGNORECASE):
            if self.on_status:
                self._safe_callback(self.on_status, "scan_status", "finish", "Pengukuran 60 detik Selesai")

        # 4. Parse Prediction Result: "HASIL: Normal" / "HASIL: Cemas" / "HASIL: Sangat Cemas"
        if "HASIL:" in msg_clean.upper():
            idx = msg_clean.upper().find("HASIL:")
            hasil_text = msg_clean[idx + 6:].strip()
            if self.on_prediction:
                self._safe_callback(self.on_prediction, hasil_text)
            if self.on_status:
                self._safe_callback(self.on_status, "prediction", "result", f"Hasil: {hasil_text}")

    def _safe_callback(self, func, *args, **kwargs):
        """Mengeksekusi callback secara thread-safe pada Flet main UI loop"""
        try:
            if self.page:
                self.page.run_task(self._async_dispatch, func, args, kwargs)
            else:
                func(*args, **kwargs)
        except Exception as e:
            print(f"[SensorService] Exception in callback dispatch: {e}")

    async def _async_dispatch(self, func, args, kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"[SensorService] Exception executing UI callback: {e}")
