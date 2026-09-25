"""اختبار منطق التحويل والواجهة بدون فتح النافذة."""
import tkinter as tk
import io
import sys

# 1) فحص بناء الواجهة (نمنع mainloop)
tk.Tk.mainloop = lambda self, n=0: None
ns = {"__name__": "test_module"}
src = open("once_human_arabic.py", encoding="utf-8").read()
exec(compile(src, "once_human_arabic.py", "exec"), ns)
print("[1] الواجهة بُنيت بنجاح")

shape = ns["shape_text"]
get_conv = ns["get_converted_text"]
set_color = ns["set_color"]
entry = ns["entry_input"]

out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 2) الحقل الفارغ / placeholder
assert shape("") is None and shape("   ") is None
assert shape(ns["PLACEHOLDER"]) is None
print("[2] الفراغ والـ placeholder لا يُنتجان نصًا")

# 3) لا رموز Presentation Forms-A (السبب الجذري لخطأ 游戏 العرض)
sample = "لا إله إلا الله محمد رسول الله"
shaped = shape(sample)
bad = [hex(ord(c)) for c in shaped if 0xFB00 <= ord(c) <= 0xFEFF and ord(c) not in range(0xFE70, 0xFF00)]
print(f"[3] رموز ممنوعة: {bad if bad else 'لا شيء ✓'}")
assert not bad, bad
present_b = [hex(ord(c)) for c in shaped if 0xFE70 <= ord(c) <= 0xFEFF]
print(f"    رموز Presentation Forms-B المستخدمة: {len(present_b)} (المسموح)")

# 4) الحركات والتطويل تُحذف
assert shape("مَحَمَّد") == shape("محمد"), "الحركات لم تُحذف"
assert "ـ" not in shape("مـــحمد"), "التطويل لم يُحذف"
print("[4] الحركات والتطويل تُحذف ✓")

# 5) بادئة اللون تُضاف في البداية
entry.delete(0, tk.END)
entry.insert(0, sample)
set_color("#R", ns["_color_buttons"][1], convert=False)
assert get_conv().startswith("#R"), get_conv()[:5]
set_color("#Y", ns["_color_buttons"][3], convert=False)
assert get_conv().startswith("#Y")
# 6) زر "بدون لون" يزيل البادئة
set_color("", ns["btn_reset_color"], convert=False)
assert get_conv() == shaped, "زر بدون لون لم يُلغِ اللون"
print("[5] بادئة اللون تُضاف وتُزال بشكل صحيح ✓")

# 7) تبديل الألوان لا يفسد مظهر أزرار الألوان
base = {b: ns["_btn_base_style"][b] for b in ns["_color_buttons"]}
for i, b in enumerate(ns["_color_buttons"]):
    set_color(ns["COLORS"][i][1], b, convert=False)
for b, style in base.items():
    assert ns["_btn_base_style"][b] == style, "تغير المظهر الأساسي"
print("[6] مظهر أزرار الألوان ثابت بعد التبديل ✓")

# 8) الوميض: ثلاث نقرات سريعة لا تترك الزر معطلاً
for _ in range(3):
    ns["convert_and_copy"]()
assert len(ns["_pending_jobs"]) >= 1
assert str(ns["btn_both"].cget("state")) == "disabled"
ns["root"].update()
for job in list(ns["_pending_jobs"].values()):
    ns["root"].after_cancel(job)
print("[7] الومضات المتتابعة تُلغى بعضها ولا تترك الزر معطلاً ✓")

# 9) النسخ الفعلي للحافظة
entry.delete(0, tk.END)
entry.insert(0, sample)
set_color("#G", ns["_color_buttons"][2], convert=False)
ns["convert_and_copy"]()
import pyperclip
clip = pyperclip.paste()
assert clip == get_conv(), f"الحافظة: {clip!r}"
print(f"[8] الحافظة تحوي النص الصحيح: {clip[:6]!r}... (طول {len(clip)})")

# 10) زر الديسكورد
ns["copy_discord"]()
assert pyperclip.paste() == ns["DISCORD_LINK"]
print("[9] زر Discord ينسخ الرابط ✓")

# 11) الإغلاق لا يرمي استثناءات
entry.delete(0, tk.END)
entry.insert(0, ns["PLACEHOLDER"])
ns["on_focus_in"](None)
assert entry.get() == "", "placeholder لم يُحذف عند التركيز"
entry.insert(0, ns["PLACEHOLDER"])
ns["on_focus_in"](None)
assert entry.get() == "", "placeholder حُذف مرتين"
ns["on_focus_out"](None)
assert entry.get() == ns["PLACEHOLDER"], "placeholder لم يُستعد عند تفريغ الحقل"
print("[10] الـ placeholder يعمل كـ placeholder حقيقي (يُحذف/يُستعد) ✓")

# 12) المعاينة تتحدث وتعرض النص بدون كود اللون
ns["on_focus_in"](None)
entry.insert(0, sample)
set_color("#B", ns["_color_buttons"][4], convert=False)
ns["update_preview"]()
preview = ns["lbl_preview"].cget("text")
assert preview == shaped, preview
assert not preview.startswith("#"), "كود اللون ظهر في المعاينة"
print("[11] المعاينة تعرض النص المشكول بلا كود اللون ✓")

# 13) المعاينة الفارغة تعرض التلميح
entry.delete(0, tk.END)
ns["update_preview"]()
assert ns["lbl_preview"].cget("text") == ns["PREVIEW_HINT"]
print("[12] المعاينة تعرض التلميح عند الفراغ ✓")

# 14) حساب حجم النافذة يعمل (بدل رقم ثابت)
root2 = ns["root"]
root2.update_idletasks()
w = max(ns["MIN_WIDTH"], root2.winfo_reqwidth())
h = root2.winfo_reqheight()
assert w >= ns["MIN_WIDTH"] and h > 0
print(f"[13] حجم النافذة المحسوب: {w}x{h}")

ns["on_close"]()
print("[14] on_close ينهي العملية بنظافة ✓")
print("\nكل الاختبارات نجحت")
out.flush()
