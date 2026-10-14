# raw-sources – الملفات الأصلية

الـ branch ده فيه **الملفات الخام بس** (PDF / DOC) اللي اتبنت منها الداتا في `main` (`data/`). مفيهوش كود ولا داتا متقسمة.

```bash
git fetch origin raw-sources
git checkout raw-sources        # أو: git worktree add ../raw raw-sources
```

| الملف | إيه | استخدمناه في |
|---|---|---|
| `raw/official/law_1_2000_gazette.pdf` | القانون 1/2000 – الجريدة الرسمية ع4 مكرر 29/1/2000 | `L1_2000` (85 مادة) |
| `raw/official/law_10_2004_gazette.pdf` | القانون 10/2004 محاكم الأسرة – الجريدة الرسمية ع12 تابع (أ) 18/3/2004 | `L10_2004` |
| `raw/official/law_25_1920_original_gazette.pdf` | 25/1920 النص الأصلي – الوقائع المصرية ع61 15/7/1920 | نسخة تاريخية |
| `raw/official/decree_1926_amend_25_1920_gazette.pdf` | مرسوم 1926 بتعديل 25/1920 – الوقائع المصرية ع54 7/6/1926 | نسخة تاريخية |
| `raw/official/law_25_1929_original_gazette.pdf` | 25/1929 النص الأصلي – الوقائع المصرية ع27 25/3/1929 | نسخة تاريخية |
| `raw/official/law_176_2020_gazette.pdf` | القانون 176/2020 (م47 من 1/2000) – الجريدة الرسمية ع36 مكرر 5/9/2020 | `L176_2020` |
| `raw/official/scc_113_26_2006_ruling.pdf` | حكم الدستورية 113/26ق (إثبات الطلاق) | flag م21 من 1/2000 |
| `raw/secondary/personal_status_laws_compilation.pdf` | تجميع 25/1920 و25/1929 بعد التعديلات (OCR) | النسخ المجمعة الساري |
| `raw/secondary/personal_status_laws_compilation_2003.doc` | تجميع Word 2003 (المواريث، الوصية، الولاية على المال، قرارات 2000) | `L119_1952`، `L71_1946`، … |
| `raw/secondary/ashraf_kamal_encyclopedia/` | موسوعة الأحوال الشخصية – أشرف مصطفى كمال (4 أجزاء) | مبادئ النقض + قرارات 2004 |
| `raw/secondary/ncw_personal_status_guide_2021.pdf` | دليل المجلس القومي للمرأة 2021 | `data/context/` |
| `raw/secondary/penal_code_2003.pdf` | قانون العقوبات (طبعة 2003) | المادتين 292 و293 |
| `raw/secondary/case_reference_10_rulings.pdf` | مرجع 10 أحكام | `rulings_index.csv` |
| `raw/draft_2026/family_law_draft_2026_with_memo.pdf` | مشروع قانون الأسرة 2026 + المذكرة الإيضاحية (217 ص) | `data/draft_2026/` |

⚠️ الريبو private: الموسوعة ودليل المجلس القومي عليهم حقوق نشر.
