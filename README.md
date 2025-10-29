# CN331_FINAL_PROJECT

## ขั้นตอนการติดตั้ง (Setup Steps)

ทำตามขั้นตอนเหล่านี้เพื่อตั้งค่าโปรเจคในเครื่องของคุณ (Local Setup)

### 1.โคลน (Clone) Repository

```bash
git clone [https://github.com/athiphatsunsit67/CN331_FINAL_PROJECT.git](https://github.com/athiphatsunsit67/CN331_FINAL_PROJECT.git)
cd CN331_FINAL_PROJECT}
```

### 2.สร้างและเปิดใช้งาน Virtual Environment

```bash
# สร้าง venv (แนะนำให้ใช้ชื่อ venv)
python -m venv venv

# เปิดใช้งาน (Activate) venv
# (Windows)
.\venv\Scripts\activate

# (macOS/Linux)
source venv/bin/activate
```

### 3.ติดตั้ง Dependencies
```bash
# ตรวจสอบว่า venv ทำงานอยู่
# แล้วสั่งติดตั้ง
pip install -r requirements.txt
```
