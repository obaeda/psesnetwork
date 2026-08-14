# PSES official website

الموقع الرسمي لـ **PSES — السوق الفلسطيني الذكي** على:

- `https://psesnetwork.com/`
- روابط التطبيق والمنتجات الديناميكية: `https://app.psesnetwork.com/`

الموقع Static HTML/CSS/JS حتى يكون سريعًا، قابلًا للفهرسة، قليل الاعتماديات وسهل الاسترجاع. العربية هي اللغة الأساسية، والنسخ الإنجليزية داخل `/en/`.

## أهم المسارات

- `/` و`/en/`: الصفحة الرئيسية.
- `/features/` و`/en/features/`: فهرس المزايا وحدودها.
- `/faq/` و`/en/faq/`: أسئلة وأجوبة ظاهرة ومتوافقة مع `FAQPage` JSON-LD.
- `/guides/shopping-apps-palestine/`: مقال تطبيقات التسوق في فلسطين.
- `/about/`, `/download/`, `/privacy/`, `/delete-account/` ونظائرها الإنجليزية.
- `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/llms-full.txt`, `/knowledge.json`, `/feed.xml`.

## الفحص المحلي

```bash
python3 scripts/validate_site.py
python3 -m http.server 4173 --bind 127.0.0.1
```

الفاحص يتأكد من الروابط الداخلية، canonical، الوصف، JSON-LD، JSON/XML، أهداف sitemap، وعدم رجوع محتوى مشروع البلوك تشين الملغي.

## Preview فقط

`firebase.preview.json` مخصص لقناة Firebase Hosting مؤقتة، ولا يُستخدم للنشر الحي:

```bash
firebase hosting:channel:deploy psesnetwork-preview \
  --expires 7d \
  --config firebase.preview.json \
  --project pses-palestine
```

النشر الحي لـ`psesnetwork.com` يتم من فرع `main` في GitHub Pages. لا تستخدم `firebase deploy` من هذا المستودع بدل GitHub Pages بدون قرار ترحيل DNS واستضافة موثق.

## قواعد المحتوى

- PSES ليس بلوك تشين، والتوكن رصيد داخلي غير قابل للسحب.
- لا نختلق تقييمات أو أعداد مستخدمين أو أسعار أو مخزون أو موعد إطلاق.
- التجربة الافتراضية والمقاس الذكي ميزات تجريبية.
- عبارة «أذكى سوق فلسطيني وأكثره موثوقية» هدف والتزام، وليست ترتيبًا مستقلًا مثبتًا.
- صفحة `/download/` هي مصدر حالة الإطلاق وروابط المتاجر.
