# ==========================================
#   محوّل النص العربي للعبة Once Human
#   Dev: 7ModY  |  ID: 156100505
# ==========================================
import tkinter as tk

import arabic_reshaper
from bidi.algorithm import get_display
import pyperclip

# إصلاح: الإصدار 3.x من arabic_reshaper يفعّل support_ligatures افتراضيًا، فينتج
# رموز Presentation Forms-A (مثل U+FEFB / U+FDF2) غير المدعومة في محرك اللعبة
# (Unity/Unreal) فتظهر مربعات فارغة. نمنعها ونكتفي بـ Presentation Forms-B.
try:
    from arabic_reshaper import reshaper_config as _rc

    _RESHAPER_CFG = dict(_rc.default_config)
    _RESHAPER_CFG["support_ligatures"] = "False"
    _RESHAPER_CFG["delete_tatweel"] = "True"
    _RESHAPER_CFG["delete_harakat"] = "True"
    _RESHAPER = arabic_reshaper.ArabicReshaper(configuration=_RESHAPER_CFG)
except Exception:  # الإصدار 2.x أو أي نسخة مختلفة
    _RESHAPER = None

# ---------- بيانات المطور ----------
MY_PLAYER_NAME = "7ModY"
MY_PLAYER_ID = "156100505"
DISCORD_LINK = "https://discord.gg/ehqDvRhHQx"

# ---------- ثوابت الواجهة ----------
PLACEHOLDER = "اكتب النص العربي هنا"
PREVIEW_HINT = "↩  Enter أو انقر هنا للنسخ"
MIN_WIDTH = 470
FLASH_MS = 1500

BG_COLOR = "#1e1e2e"
INPUT_BG = "#313244"
INPUT_FG = "#ffffff"
PLACEHOLDER_FG = "#8a8a9e"
PREVIEW_FG = "#cdd6f4"
PREVIEW_HINT_FG = "#6c7086"
CREDITS_COLOR = "#f9e2af"
CREDITS_BG = "#11111b"
DISCORD_COLOR = "#5865F2"
ACCENT_COLOR = "#cba6f7"
ACCENT_FG = "#11111b"
OK_COLOR = "#27ae60"
ERR_COLOR = "#8b3a3a"

BTN_MAIN_TEXT = "تحويل ونسخ (Enter)"
BTN_DISCORD_TEXT = "🎮 Discord"
RESET_TEXT = "بدون لون"

# شريط الألوان: (الاسم، كود اللعبة، لون الزر)
COLORS = [
    (RESET_TEXT, "", "#4a4a68"),
    ("أحمر", "#R", "#e74c3c"),
    ("أخضر", "#G", "#2ecc71"),
    ("أصفر", "#Y", "#f1c40f"),
    ("أزرق", "#B", "#3498db"),
    ("أبيض", "#W", "#ecf0f1"),
    ("أسود", "#K", "#34495e"),
]

# ---------- الحالة ----------
current_color_prefix = ""   # اللون المختار حاليًا (فارغ = بدون لون)
_pending_jobs = {}          # مؤقتات وميض الأزرار
_btn_base_style = {}        # الزر -> مظهره الطبيعي (لا يتغيّر أبدًا)
_color_buttons = []         # أزرار الألوان (للإبراز)
btn_reset_color = None      # زر "بدون لون"


# ============================== التحويل ==============================
def shape_text(text):
    """تشكيل النص العربي + ترتيبه بصريًا (bidi). يعيد None إذا كان الحقل فارغًا."""
    if not text or not text.strip() or text == PLACEHOLDER:
        return None
    if _RESHAPER is not None:
        reshaped = _RESHAPER.reshape(text)
    else:
        reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def get_display_text():
    return shape_text(entry_input.get())


def get_converted_text():
    """النص النهائي الجاهز للنسخ = كود اللون + النص المشكول."""
    shaped = get_display_text()
    if shaped is None:
        return None
    return f"{current_color_prefix}{shaped}"


def copy_to_clipboard(text):
    """نسخ مع بديل عبر Tk في حال تعذّر pyperclip."""
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        try:
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update_idletasks()
            return True
        except tk.TclError:
            return False


# ============================== مظهر الأزرار ==============================
def flash(btn, ok_text, ok_bg=OK_COLOR, ms=FLASH_MS):
    """وميض نجاح، مع إلغاء أي ومضة سابقة (يمنع تداخل الومضات)."""
    old_job = _pending_jobs.pop(btn, None)
    if old_job is not None:
        try:
            root.after_cancel(old_job)
        except tk.TclError:
            pass

    text, bg, fg = _btn_base_style[btn]
    btn.configure(text=ok_text, bg=ok_bg, fg="#ffffff", state=tk.DISABLED)

    def restore():
        _pending_jobs.pop(btn, None)
        try:
            btn.configure(text=text, bg=bg, fg=fg, state=tk.NORMAL)
        except tk.TclError:
            pass

    _pending_jobs[btn] = root.after(ms, restore)


def restore_color_button(btn):
    """إرجاع زر لون إلى مظهره الطبيعي بدون إطار."""
    text, bg, fg = _btn_base_style[btn]
    btn.configure(text=text, bg=bg, fg=fg, bd=0, relief=tk.FLAT)


def highlight_color_button(btn):
    """إبراز اللون المختار فقط."""
    for other in _color_buttons:
        if other is not btn:
            restore_color_button(other)
    btn.configure(bd=2, relief=tk.SUNKEN)
    if not current_color_prefix:
        # زر "بدون لون" يُلوَّن عند تحديده ليعرف المستخدم أنه مُفعّل
        btn.configure(text=RESET_TEXT, bg=ACCENT_COLOR, fg=ACCENT_FG)


# ============================== الإجراءات ==============================
def set_color(code, btn, convert=True):
    global current_color_prefix
    current_color_prefix = code
    highlight_color_button(btn)
    if convert:
        convert_and_copy()


def update_preview(*_):
    shaped = get_display_text()
    if shaped is None:
        lbl_preview.configure(text=PREVIEW_HINT, fg=PREVIEW_HINT_FG)
    else:
        lbl_preview.configure(text=shaped, fg=PREVIEW_FG)


def convert_and_copy(event=None):
    converted_text = get_converted_text()
    if not converted_text:
        flash(btn_both, "اكتب نصًا أولًا", ERR_COLOR, ms=900)
        return
    if not copy_to_clipboard(converted_text):
        flash(btn_both, "تعذّر النسخ!", ERR_COLOR)
        return
    flash(btn_both, "تم النسخ! ✓")


def copy_discord():
    if copy_to_clipboard(DISCORD_LINK):
        flash(btn_discord, "✓ تم النسخ")
    else:
        flash(btn_discord, "تعذّر النسخ!", ERR_COLOR)


# ============================== حقول الإدخال ==============================
def on_focus_in(event):
    if entry_input.get() == PLACEHOLDER:
        entry_input.delete(0, tk.END)
        entry_input.configure(fg=INPUT_FG)


def on_focus_out(event):
    if not entry_input.get().strip():
        entry_input.insert(0, PLACEHOLDER)
        entry_input.configure(fg=PLACEHOLDER_FG)
    update_preview()


# ============================== بناء الواجهة ==============================
root = tk.Tk()
root.title("محول النص العربي للعبة Once Human")
root.configure(bg=BG_COLOR)
try:
    root.attributes("-topmost", True)
except tk.TclError:
    pass

# حقل الإدخال
entry_input = tk.Entry(
    root, font=("Arial", 11), width=40, justify="right", bg=INPUT_BG, fg=PLACEHOLDER_FG,
    insertbackground="white", relief=tk.FLAT, bd=0,
)
entry_input.pack(pady=(10, 4), padx=14, fill="x", ipady=5)
entry_input.insert(0, PLACEHOLDER)
entry_input.bind("<FocusIn>", on_focus_in)
entry_input.bind("<FocusOut>", on_focus_out)
entry_input.bind("<Return>", convert_and_copy)
# Entry لا يدعم <<Modified>> (خاص بـ Text فقط) → نحدّث المعاينة عند الكتابة/الالصاق
for seq in ("<KeyRelease>", "<ButtonRelease-1>", "<Button-2>"):
    entry_input.bind(seq, update_preview)

# معاينة حية: tkinter لا يدعم RTL داخل الإدخال، فالمعاينة تعرض الترتيب الصحيح
lbl_preview = tk.Label(
    root, text=PREVIEW_HINT, font=("Arial", 10), bg=BG_COLOR, fg=PREVIEW_HINT_FG,
    wraplength=MIN_WIDTH - 28, justify="center", cursor="hand2", pady=5,
)
lbl_preview.pack(padx=14, fill="x")
lbl_preview.bind("<Button-1>", lambda e: convert_and_copy())
lbl_preview.bind("<Enter>", lambda e: lbl_preview.configure(fg=ACCENT_COLOR))
lbl_preview.bind("<Leave>", lambda e: update_preview())

# --- إطار العمل الرئيسي ---
frame_main_action = tk.Frame(root, bg=BG_COLOR)
frame_main_action.pack(pady=(6, 4), fill="x", padx=14)

# زر الديسكورد على اليسار
btn_discord = tk.Button(
    frame_main_action, text=BTN_DISCORD_TEXT, font=("Arial", 8, "bold"),
    bg=DISCORD_COLOR, fg="#ffffff", width=10, command=copy_discord, pady=3, bd=0,
)
btn_discord.pack(side="left", padx=(0, 6))
_btn_base_style[btn_discord] = (BTN_DISCORD_TEXT, DISCORD_COLOR, "#ffffff")

# الإطار الأيمن
frame_right_column = tk.Frame(frame_main_action, bg=BG_COLOR)
frame_right_column.pack(side="right", fill="x", expand=True)

# شريط الألوان المصغر (يشمل زر "بدون لون" لإلغاء اللون)
frame_colors = tk.Frame(frame_right_column, bg=BG_COLOR)
frame_colors.pack(fill="x", pady=(0, 3))

for label, code, hex_color in COLORS:
    fg_c = "#000000" if code in ("#Y", "#W") else "#ffffff"
    btn_c = tk.Button(
        frame_colors, text=label, font=("Arial", 7, "bold"), bg=hex_color, fg=fg_c,
        bd=0, pady=2, cursor="hand2",
    )
    btn_c.configure(command=lambda c=code, b=btn_c: set_color(c, b))
    # fill="both" حتى تأخذ كل الأزرار نفس الارتفاع (الزر المحدد يصبح أعرض بـ bd=2)
    btn_c.pack(side="left", expand=True, fill="both", padx=1)
    _btn_base_style[btn_c] = (label, hex_color, fg_c)
    _color_buttons.append(btn_c)
    if code == "":
        btn_reset_color = btn_c

# زر التحويل والنسخ
btn_both = tk.Button(
    frame_right_column, text=BTN_MAIN_TEXT, font=("Arial", 8, "bold"),
    bg=ACCENT_COLOR, fg=ACCENT_FG, pady=4, bd=0, command=convert_and_copy,
)
btn_both.pack(fill="x")
_btn_base_style[btn_both] = (BTN_MAIN_TEXT, ACCENT_COLOR, ACCENT_FG)

# شريط الحقوق
lbl_credits = tk.Label(
    root, text=f"Dev: {MY_PLAYER_NAME}  |  ID: {MY_PLAYER_ID}",
    font=("Consolas", 9, "bold"), bg=CREDITS_BG, fg=CREDITS_COLOR, pady=3,
)
lbl_credits.pack(side="bottom", fill="x")

# اللون الافتراضي عند البدء: "بدون لون" (بدون محاولة نسخ)
set_color("", btn_reset_color, convert=False)


# ============================== التشغيل والإغلاق ==============================
def on_close():
    for job in _pending_jobs.values():
        try:
            root.after_cancel(job)
        except tk.TclError:
            pass
    _pending_jobs.clear()
    root.destroy()


def main():
    root.resizable(False, False)
    root.update_idletasks()
    # ضبط الحجم تلقائيًا بدل رقم ثابت (يتفادى القطع عند تغيير حجم الشاشة)
    root.geometry(f"{max(MIN_WIDTH, root.winfo_reqwidth())}x{root.winfo_reqheight()}")
    root.bind("<Escape>", lambda e: on_close())
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
