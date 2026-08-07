#!/usr/bin/env python3
import asyncio
import time
import threading
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "physioanx"
TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class BLEReceiver:
    def __init__(self, callback_func=None):
        self.callback_func = callback_func
        self.is_running = False

    def _handle_notification(self, sender, data: bytearray):
        message = data.decode('utf-8', errors='ignore').strip()
        if message:
            if self.callback_func:
                self.callback_func(message)

    async def _listen_loop(self):
        self.is_running = True
        print(f"Mencari Bluetooth '{DEVICE_NAME}'...")
        while self.is_running:
            try:
                device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=5.0)
                if not device:
                    await asyncio.sleep(3)
                    continue

                print(f"Terhubung dengan alat Raspberry Pi: {device.name} [{device.address}]\n")
                async with BleakClient(device.address, timeout=10.0) as client:
                    if client.is_connected:
                        try:
                            services = await client.get_services()
                        except Exception:
                            services = client.services

                        print(f"Terhubung dengan alat Raspberry Pi: {device.name} [{device.address}]")
                        print("Membaca layanan & karakteristik GATT...")

                        target_char_obj = None
                        target_uuid_clean = TX_CHAR_UUID.lower().replace("-", "")
                        notify_candidates = []
                        found_chars_log = []

                        for service in services:
                            for char in service.characteristics:
                                char_uuid_clean = char.uuid.lower().replace("-", "")
                                props = [str(p).lower() for p in char.properties]
                                char_info = f"{char.uuid} ({','.join(props)})"
                                found_chars_log.append(char_info)

                                if char_uuid_clean == target_uuid_clean or "6e400003" in char_uuid_clean:
                                    target_char_obj = char
                                    break
                                elif any(p in props for p in ["notify", "indicate"]):
                                    notify_candidates.append(char)
                            if target_char_obj:
                                break

                        if not target_char_obj and notify_candidates:
                            target_char_obj = notify_candidates[0]
                            print(f"[BLE] TX_CHAR_UUID persis tidak ditemukan. Menggunakan karakteristik notify/indicate: {target_char_obj.uuid}")

                        if target_char_obj:
                            print(f"[BLE] Subscribing ke karakteristik: {target_char_obj.uuid}")
                            await client.start_notify(target_char_obj, self._handle_notification)
                            while client.is_connected and self.is_running:
                                await asyncio.sleep(1)
                        else:
                            chars_str = ", ".join(found_chars_log) if found_chars_log else "Tidak ada"
                            print(f"[BLE ERROR] Karakteristik {TX_CHAR_UUID} tidak ditemukan pada {device.name}. Karakteristik yang ditemukan: [{chars_str}]")
                            await asyncio.sleep(5)
            except Exception as e:
                print(f"[BLE ERROR] {e}")
            await asyncio.sleep(3)

    def start_background(self):
        def _thread_target():
            asyncio.run(self._listen_loop())
        thread = threading.Thread(target=_thread_target, daemon=True)
        thread.start()
        return thread

def display_clean_output(msg: str):
    if "HASIL:" in msg:
        print("\n" + "=" * 50)
        print(f"  {msg}")
        print("=" * 50 + "\n")
    elif "Scanning" in msg or "Tombol" in msg:
        print(f">> {msg}")
    elif "Finish" in msg:
        print(f">> {msg}\n")
    elif "HR:" in msg:
        print(f"   {msg}")
    else:
        print(f"{msg}")

if __name__ == "__main__":
    print("=" * 50)
    print(" PHYSIOANX TERMINAL MONITOR")
    print("=" * 50)

    receiver = BLEReceiver(callback_func=display_clean_output)
    receiver.start_background()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Terminal dihentikan.")
