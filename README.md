# محوّل النص العربي للعبة Once Human

<div align="right">

برنامج صغير يحل مشكلة معروفة: **محركات الألعاب (Unity/Unreal) لا تدعم تشكيل الحروف العربية**، فتكتب النص العربي داخل اللعبة فيظهر مربعات فارغة `□□□` أو حروف مقطّعة. هذا البرنامج يحوّل النص إلى الشكل الذي تعرضه اللعبة بشكل صحيح، وينسخه للحافظة بضغطة واحدة.

</div>

---

## ✅ تحميل مباشر

**[⬇️ تحميل من صفحة الإصدارات (Releases)](https://github.com/MF7Sha/once-human/releases)**

الإصدار الحالي: [`v1.0.0`](https://github.com/MF7Sha/once-human/releases/tag/v1.0.0) — ملف `OnceHumanArabic.exe` (ملف واحد، لا يحتاج تثبيت)

---

## 🚀 طريقة الاستخدام

1. شغّل `OnceHumanArabic.exe`.
2. اكتب النص العربي في الحقل العلوي.
3. اختر اللون المطلوب (أو **بدون لون**).
4. اضغط **Enter** أو زر `تحويل ونسخ` — النص جاهز في الحافظة.
5. افتح دردشة اللعبة والصق بـ `Ctrl + V`.

> النص يُنسخ تلقائيًا عند اختيار اللون أيضًا.
> أسفل الحقل توجد **معاينة حيّة** تعرض النص بالشكل النهائي قبل النسخ.

### ⌨️ الاختصارات

| المفتاح | الوظيفة |
|---|---|
| `Enter` | تحويل ونسخ |
| `Esc` | إغلاق البرنامج |

### 🎨 أكواد الألوان

| اللون | الكود |
|---|---|
| بدون لون | *(فارغ)* |
| أحمر | `#R` |
| أخضر | `#G` |
| أصفر | `#Y` |
| أزرق | `#B` |
| أبيض | `#W` |
| أسود | `#K` |

---

## 🐛 المشكلة التي يحلها هذا البرنامج

مكتبة `arabic-reshaper` في إصدارها 3.x تفعّل `support_ligatures` **افتراضيًا**، فتحوّل الكلمات إلى رموز من نوع **Presentation Forms-A** — وهي روابط خط (Glyph IDs) لا يعرفها محرك اللعبة:

| النص | الناتج الافتراضي | ما يراه اللاعب في اللعبة |
|---|---|---|
| `لا` | `U+FEFB` | مربع فارغ ☐ |
| `الله` | `U+FDF2` | مربع فارغ ☐ |

لذلك يستخدم البرنامج مُعيد تشكيل مخصصًا يفرض `support_ligatures = False`، فيُنتج رموز **Presentation Forms-B** فقط:

```python
from arabic_reshaper import reshaper_config

cfg = dict(reshaper_config.default_config)
cfg["support_ligatures"] = "False"   # ← هذا هو السطر المهم
cfg["delete_tatweel"] = "True"
cfg["delete_harakat"] = "True"
reshaper = arabic_reshaper.ArabicReshaper(configuration=cfg)
```

كما يحذف البرنامج الحركات والتطويل لأن اللعبة لا تحتاجهما.

---

## 🛠️ البناء من المصدر

يتطلب [Python 3.10+](https://www.python.org/downloads/).

```bash
git clone https://github.com/MF7Sha/once-human.git
cd once-human
pip install -r requirements.txt
python once_human_arabic.py
```

### بناء ملف exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --clean ^
  --name "OnceHumanArabic" ^
  --version-file "version_info.txt" ^
  once_human_arabic.py
```

الناتج في مجلد `dist/`.

### تشغيل الاختبارات

```bash
python test_logic.py
```

يغطي 14 حالة: التشكيل، منع رموز Forms-A، حذف الحركات، بادئة اللون وإلغاؤها، تداخل وميض الأزرار، الحافظة، الـ placeholder، وحساب حجم النافذة.

---

## 📁 بنية المشروع

```
once-human/
├── once_human_arabic.py    # البرنامج كاملًا
├── test_logic.py           # اختبارات المنطق (14 حالة)
├── requirements.txt        # المكتبات المطلوبة
├── version_info.txt        # معلومات إصدار ملف exe
├── OnceHumanArabic.spec    # إعدادات PyInstaller
└── dist/
    └── OnceHumanArabic.exe # البرنامج الجاهز للتحميل
```

---

## 🛡️ ملاحظات

- البرنامج **بدون إنترنت** ولا يجمع أي بيانات — كل المعالجة محلية.
- النافذة تبقى فوق غيرها (`-topmost`) لسهولة الوصول أثناء اللعب.
- يقبل النص العربي والإنجليزي والأرقام والرموز.

---

## 👨‍💻 المطور

| | |
|---|---|
| **الاسم** | 7ModY |
| **ID** | 156100505 |
| **Discord** | [انضم للسيرفر](https://discord.gg/ehqDvRhHQx) |

---

## 📄 الرخصة

MIT — انظر [`LICENSE`](LICENSE).

---

<div align="right">

## English

A small tool that fixes a common problem: **game engines (Unity/Unreal) don't shape Arabic script**, so Arabic typed in-game chat shows as empty boxes. This tool reshapes the text into the form the game renders correctly and copies it to your clipboard in one click.

- **Download:** [Releases page](https://github.com/MF7Sha/once-human/releases)
- **No internet required** — all processing is local.
- Key fix: forces `support_ligatures = False` in `arabic-reshaper` so the output uses only Presentation Forms-B, which Unity/Unreal can render.

**Dev:** 7ModY · ID: 156100505 · [Discord](https://discord.gg/ehqDvRhHQx)

</div>
