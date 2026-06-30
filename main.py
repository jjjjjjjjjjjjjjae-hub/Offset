import os
import zipfile
import sys

def find_so_files(apk_path):
    """APK ішінен барлық .so файлдарды табады"""
    so_files = []
    with zipfile.ZipFile(apk_path, 'r') as archive:
        for file in archive.namelist():
            if file.endswith('.so'):
                so_files.append(file)
    return so_files

def search_hex_pattern(apk_path, so_inner_path, hex_pattern):
    """Таңдалған .so файлының ішінен Hex паттернді іздейді"""
    # Жолдағы бос орындарды тазалау
    hex_pattern = hex_pattern.replace(" ", "")
    try:
        byte_pattern = bytes.fromhex(hex_pattern)
    except ValueError:
        print("Қате: Шеpattern-де қате бар! Тек Hex формат (мысалы: 7F 45 4C 46) болуы керек.")
        return

    print(f"\n📦 '{so_inner_path}' файлы өңделуде...")
    
    with zipfile.ZipFile(apk_path, 'r') as archive:
        with archive.open(so_inner_path) as so_file:
            # Файлды толық оқу (жадқа жүктеу)
            content = so_file.read()
            
            # Байттарды іздеу
            offset = content.find(byte_pattern)
            
            if offset != -1:
                print(f"✅ ОФСЕТ ТАБЫЛДЫ!")
                print(f"📍 Мекенжайы (Offset): {hex(offset).upper()}")
                # Келесі сәйкестіктер бар ма, тексеру
                count = 0
                while offset != -1:
                    count += 1
                    offset = content.find(byte_pattern, offset + 1)
                if count > 1:
                    print(f"ℹ️ Бұл паттерн файл ішінде тағы {count - 1} рет кездеседі.")
            else:
                print("❌ Өкінішке орай, бұл паттерн табылмады.")

def main():
    if len(sys.argv) < 2:
        print("Қате: APK файлдың аты жазылмады!")
        sys.exit(1)
        
    apk_path = sys.argv[1]
    
    if not os.path.exists(apk_path):
        print(f"Қате: '{apk_path}' файлы табылмады!")
        sys.exit(1)

    print("🔍 APK файлы анықталды. Ішіндегі кітапханалар тексерілуде...")
    so_files = find_so_files(apk_path)
    
    if not so_files:
        print("Ресурстар ішінен .so файлдары табылмады.")
        return

    print(f"Табылған .so файлдар саны: {len(so_files)}")
    
    # СЕН ІЗДЕГІҢ КЕЛЕТІН HEX ПАТТЕРН (Осы жерді өзгертуге болады)
    # Мысалы, төменде ELF файлының басы (базалық паттерн) тұр: "7F 45 4C 46"
    target_pattern = "7F 45 4C 46" 
    
    # libil2cpp.so файлын автоматты түрде іздеу
    target_so = None
    for so in so_files:
        if "libil2cpp.so" in so and "arm64-v8a" in so: # 64-биттік нұсқасы
            target_so = so
            break
            
    if not target_so:
        # Егер 64-бит табылмаса, кез келген бірінші libil2cpp.so-ны аламыз
        for so in so_files:
            if "libil2cpp.so" in so:
                target_so = so
                break

    if target_so:
        search_hex_pattern(apk_path, target_so, target_pattern)
    else:
        print("Ескерту: Скрипт 'libil2cpp.so' файлын таппады, бірінші кездескен файл тексеріледі:")
        search_hex_pattern(apk_path, so_files[0], target_pattern)

if __name__ == "__main__":
    main()
