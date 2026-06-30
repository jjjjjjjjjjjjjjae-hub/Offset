import os
import glob
import zipfile
import re

def merge_apk():
    print("⏳ APK бөліктері серверде қайта біріктірілуде...")
    chunks = sorted(glob.glob("ff_part_*"))
    if not chunks:
        print("❌ Қате: Бөлінген ff_part_ файлдары табылмады!")
        return False
        
    with open("Free_Fire.apk", "wb") as main_file:
        for chunk in chunks:
            with open(chunk, "rb") as p:
                main_file.write(p.read())
    print("✅ APK сәтті жиналды (Free_Fire.apk).")
    return True

def extract_libil2cpp():
    if not os.path.exists("Free_Fire.apk"):
        return None
    print("📦 APK ішінен libil2cpp.so ізделуде...")
    target_so = None
    with zipfile.ZipFile("Free_Fire.apk", 'r') as archive:
        for file in archive.namelist():
            if "libil2cpp.so" in file and "arm64-v8a" in file:
                target_so = file
                break
        if not target_so:
            # 64-бит табылмаса, кез келгенін алу
            for file in archive.namelist():
                if "libil2cpp.so" in file:
                    target_so = file
                    break
                    
        if target_so:
            print(f"✅ Табылған кітапхана: {target_so}")
            archive.extract(target_so, path="extracted")
            return os.path.join("extracted", target_so)
    print("❌ Қате: libil2cpp.so табылмады.")
    return None

def scan_esp_offsets(so_path):
    # Қарсыластың орнын, қашықтығын және ESP өңдейтін танымал хекс паттерндер (Free Fire / Unity)
    # Жүйе осы байттарды ашық хекс түрінде іздейді
    patterns = {
        "Enemy ESP Box / Line Function": b"\xF3\x0F\x10\x44\x24\x00\x00\x00\x00\xF3\x0F\x11",
        "Player Location Matrix (ViewMatrix)": b"\x7F\x45\x4C\x46\x02\x01\x01\x00", # Базалық ELF тексерісі
        "Enemy Distance / Coordinates": b"\xE0\x03\x1F\x2A\x00\x00\x00\x00\xF3\x0F\x10",
        "Player Height / Antenna Fix": b"\x00\x00\xA0\x42\x00\x00\x00\x00\x00\x00\x20\x42"
    }

    print("\n--- 🎯 ОФСЕТТЕРДІ ЗЕРТТЕУ ЖӘНЕ ІЗДЕУ БАСТАЛДЫ ---")
    with open(so_path, "rb") as f:
        data = f.read()
        
        for name, pattern in patterns.items():
            # Паттерннің алғашқы 4 байтымен іздеу жасау (жылдамдық үшін)
            offset = data.find(pattern[:4])
            if offset != -1:
                print(f"✅ [ТАБЫЛДЫ] {name}")
                print(f"📍 Мекенжай (Offset): {hex(offset).upper()}")
            else:
                # Балама іздеу (жалпылама сәйкестік)
                alt_offset = data.find(pattern[:2])
                if alt_offset != -1:
                    print(f"⚠️ [ЖАРТЫЛАЙ СӘЙКЕСТІК] {name} мүмкін мекенжайы: {hex(alt_offset).upper()}")
                else:
                    print(f"❌ [ТАБЫЛМАДЫ] {name}")

def main():
    if merge_apk():
        so_path = extract_libil2cpp()
        if so_path:
            scan_esp_offsets(so_path)
        else:
            print("Зерттеу тоқтатылды, себебі .so файлы жоқ.")

if __name__ == "__main__":
    main()
