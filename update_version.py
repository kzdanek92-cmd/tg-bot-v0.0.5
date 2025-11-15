#!/usr/bin/env python3
"""
Auto-update version in README and other files
Использование: python update_version.py 0.0.6 "Description of changes"
"""

import sys
import re
from datetime import datetime
from pathlib import Path

def get_current_version():
    """Получить текущую версию из README"""
    readme = Path("README.md").read_text()
    match = re.search(r'![Version]\(https://img\.shields\.io/badge/version-([0-9.]+)-blue\)', readme)
    return match.group(1) if match else None

def update_readme(new_version, description):
    """Обновить README с новой версией"""
    readme_path = Path("README.md")
    content = readme_path.read_text()
    
    current_date = datetime.now().strftime("%d %B %Y")
    
    # Обновить бейдж версии
    content = re.sub(
        r'![Version]\(https://img\.shields\.io/badge/version-[0-9.]+-blue\)',
        f'![Version](https://img.shields.io/badge/version-{new_version}-blue)',
        content
    )
    
    # Обновить дату последнего обновления
    content = re.sub(
        r'\*\*Последнее обновление:\*\* [^\\n]+',
        f'**Последнее обновление:** {current_date}',
        content
    )
    
    # Вставить новую версию в историю
    new_section = f"""### v{new_version} — "{description}" 
**Дата: {current_date}**

**Что добавлено:**
- ✅ (Описание будет добавлено)

**Статус:** 🟢 Production Ready

---

"""
    
    # Найти место для вставки новой версии (после v0.0.5)
    pattern = r'(### v[0-9.]+ — "Full Payments & Integration Update" 🚀\n\*\*Дата: [^\\n]+\*\*)'
    content = re.sub(pattern, new_section + r'\1', content)
    
    # Обновить дату в конце файла
    content = re.sub(
        r'\*Последнее обновление: [^,]+, версия [0-9.]+\*',
        f'*Последнее обновление: {current_date}, версия {new_version}*',
        content
    )
    
    readme_path.write_text(content)
    print(f"✅ README.md обновлен (версия {new_version})")

def update_config(new_version):
    """Обновить config.py"""
    config_path = Path("bot_v0.0.2/config.py")
    if config_path.exists():
        content = config_path.read_text()
        content = re.sub(
            r'VERSION = "[0-9.]+"',
            f'VERSION = "{new_version}"',
            content
        )
        config_path.write_text(content)
        print(f"✅ config.py обновлен")

def update_package_json(new_version):
    """Обновить package.json если существует"""
    package_path = Path("package.json")
    if package_path.exists():
        import json
        data = json.loads(package_path.read_text())
        data["version"] = new_version
        package_path.write_text(json.dumps(data, indent=2))
        print(f"✅ package.json обновлен")

def main():
    if len(sys.argv) < 2:
        print("Использование: python update_version.py <новая_версия> [описание]")
        print("Пример: python update_version.py 0.0.6 'Refunds & Analytics'")
        sys.exit(1)
    
    new_version = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else "New Release"
    
    current_version = get_current_version()
    print(f"📝 Обновление версии: {current_version} → {new_version}")
    print(f"📋 Описание: {description}")
    
    # Валидация версии
    if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+$', new_version):
        print("❌ Версия должна быть в формате X.Y.Z (например, 0.0.6)")
        sys.exit(1)
    
    update_readme(new_version, description)
    update_config(new_version)
    update_package_json(new_version)
    
    print(f"\n✅ Версия успешно обновлена до {new_version}!")
    print("\n📌 Следующие шаги:")
    print("1. git add .")
    print("2. git commit -m 'Release v{}' ".format(new_version))
    print("3. git tag v{}".format(new_version))
    print("4. git push origin main --tags")

if __name__ == "__main__":
    main()
