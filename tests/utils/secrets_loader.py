# secrets_loader.py

import json
from pathlib import Path

def load_secrets(file_name="secrets.json"):
    """
    טוענת את נתוני התצורה מקובץ JSON באמצעות חישוב נתיב מוחלט.
    הקוד מניח שהקובץ secrets.json נמצא בשורש הפרויקט, שתי רמות מעל קובץ זה.
    """
    
    # 1. קביעת הנתיב המוחלט של קובץ secrets_loader.py
    script_path = Path(__file__).resolve() 
    
    # 2. חישוב שורש הפרויקט (עולים מ-utils/ ל-tests/ ואז ל-SELENIUM SCRIPTS/)
    # אם הקובץ נמצא ב-tests/utils/, עלינו לעלות שתי רמות.
    project_root = script_path.parent.parent.parent # ⬅️ תיקון: 3 רמות אם הקובץ נמצא ב-tests/utils/
    
    # *הערה:* מאחר והמבנה הוא SELENIUM SCRIPTS -> tests -> utils -> secrets_loader.py, 
    # אנו צריכים לעלות 3 רמות כדי להגיע לשורש (SELENIUM SCRIPTS).
    
    
    # 3. בניית הנתיב המלא לקובץ secrets.json
    file_path = project_root / file_name
    
    # הדפסת הנתיב שמועבר ל-open()
    print(f"*** מנסה לטעון נתונים מנתיב מוחלט: {file_path}") 
    
    try:
        # פתיחת הקובץ
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ שגיאה: קובץ {file_path} לא נמצא. ודא שהוא נמצא בשורש הפרויקט.")
        return None
    except json.JSONDecodeError:
        print(f"❌ שגיאה: קובץ {file_path} אינו בפורמט JSON תקין. ודא שאינו ריק.")
        return None

# --- בדיקת תקינות ---
if __name__ == '__main__':
    data = load_secrets()
    if data:
        print("\n✅ טעינת secrets עברה בהצלחה!")