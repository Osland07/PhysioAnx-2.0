#!/usr/bin/env python3
import asyncio
import threading
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "physioanx"
TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class BLEReceiver:
    def __init__(self, callback_func=None, status_callback=None):
        self.callback_func = callback_func
        self.status_callback = status_callback
        self.is_running = False
        self.is_connected = False
        self.device_address = None
        self._thread = None

    def _notify_status(self, status: str, detail: str = ""):
        if self.status_callback:
            try:
                self.status_callback(status, detail)
            except Exception as e:
                print(f"[BLEReceiver] Error in status callback: {e}")

    def _handle_notification(self, sender, data: bytearray):
        message = data.decode('utf-8', errors='ignore').strip()
        if message:
            print(f"[BLEReceiver] Data received: {message}")
            if self.callback_func:
                try:
                    self.callback_func(message)
                except Exception as e:
                    print(f"[BLEReceiver] Error in data callback: {e}")

    async def _listen_loop(self):
        self.is_running = True
        print(f"[BLEReceiver] Mencari Bluetooth '{DEVICE_NAME}'...")
        self._notify_status("searching", f"Mencari Bluetooth '{DEVICE_NAME}'...")

        while self.is_running:
            try:
                device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=5.0)
                if not device:
                    self.is_connected = False
                    self._notify_status("searching", f"Mencari Bluetooth '{DEVICE_NAME}'...")
                    await asyncio.sleep(3)
                    continue

                self.device_address = device.address
                print(f"[BLEReceiver] Terhubung dengan Raspberry Pi: {device.name} [{device.address}]\n")
                self.is_connected = True
                self._notify_status("connected", f"Terhubung dengan {device.name}")

                async with BleakClient(device.address, timeout=10.0) as client:
                    if client.is_connected:
                        try:
                            services = await client.get_services()
                        except Exception:
                            services = client.services

                        print(f"[BLEReceiver] Terhubung ke {device.name}. Membaca layanan & karakteristik GATT...")
                        
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
                            print(f"[BLEReceiver] TX_CHAR_UUID persis tidak ditemukan. Menggunakan karakteristik notify/indicate: {target_char_obj.uuid}")

                        if target_char_obj:
                            print(f"[BLEReceiver] Subscribing ke karakteristik: {target_char_obj.uuid}")
                            await client.start_notify(target_char_obj, self._handle_notification)

                            while client.is_connected and self.is_running:
                                await asyncio.sleep(1)
                        else:
                            chars_str = ", ".join(found_chars_log) if found_chars_log else "Tidak ada"
                            err_msg = f"Karakteristik {TX_CHAR_UUID} tidak ditemukan pada '{device.name}'. Karakteristik yang ditemukan: [{chars_str}]"
                            print(f"[BLEReceiver] {err_msg}")
                            self._notify_status("disconnected", err_msg)
                            await asyncio.sleep(5)

                self.is_connected = False
                self._notify_status("disconnected", "Terputus dari device Bluetooth")
            except Exception as e:
                self.is_connected = False
                print(f"[BLEReceiver] Loop error: {e}")
                self._notify_status("disconnected", f"Koneksi terputus: {e}")

            if self.is_running:
                await asyncio.sleep(3)

    def start_background(self):
        if self.is_running:
            return self._thread

        def _thread_target():
            asyncio.run(self._listen_loop())

        self._thread = threading.Thread(target=_thread_target, daemon=True)
        self._thread.start()
        return self._thread

    def stop(self):
        self.is_running = False
        self.is_connected = False
        self._notify_status("stopped", "Receiver dihentikan")
