"""Build the standalone Jupyter Notebook lesson page.

The page is intentionally separate from the React DSS app. It should feel like
reading a Jupyter notebook, not like another product dashboard.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "bus_delay_full_journey_expanded.ipynb"
OUTPUT = ROOT / "frontend" / "public" / "jupyter-notebook.html"


INTRO = """
هذه الصفحة ليست شاشة Dashboard وليست اختبارا للطلاب. هي نسخة قراءة من Jupyter Notebook تشرح كيف يتحول مشروع Bus Delay DSS من فكرة إلى كود قابل للتشغيل. لذلك تم ترتيبها مثل notebook حقيقي: خلية شرح، ثم خلية كود، ثم مخرج متوقع، ثم شرح معنى المخرج.

الهدف أن يقرأ الطالب الكود وهو يعرف لماذا يوجد كل جزء. لا يكفي أن يرى دالة باسم generate_dataset أو analyze_dataset؛ يجب أن يفهم ما الذي يدخل إليها، ما الذي يخرج منها، كيف يؤثر ذلك على Backend API، وكيف يظهر لاحقا في واجهة DSS.
"""


WEEK_GUIDANCE = {
    1: {
        "phase": "التأسيس وفهم البيانات",
        "label": "Week 1 - Data foundation",
        "summary": "يبني الطالب الصورة الأولى: ما القرار الذي يخدمه النظام، ما شكل البيانات، وما معنى سؤال: ماذا يمثّل الصف الواحد؟",
        "know": [
            "معنى decision scope ولماذا لا يبدأ DSS من الرسم أو الواجهة فقط.",
            "معنى ماذا يمثّل الصف الواحد؟ في routes وstops وtrips وstop_events، ولماذا يختلف صف الرحلة عن صف توقف الحافلة.",
            "كيف تتحول config إلى قواعد توليد بيانات يمكن تعديلها وفحص أثرها.",
        ],
        "execute": [
            "تشغيل خلايا project context وconfig وgenerate_dataset بالترتيب.",
            "فتح عينات الجداول ومراجعة المفاتيح والحقول قبل بناء أي KPI.",
            "مطابقة stop_events مع trips وstops حتى يرى الطالب العلاقة بين الصفوف.",
        ],
        "test": [
            "التأكد من عدد الجداول والصفوف المتوقع بعد التوليد.",
            "تغيير قيمة صغيرة في config وملاحظة أثرها على البيانات الناتجة.",
            "التأكد أن كل stop_event يشير إلى trip وstop موجودين.",
        ],
        "report": [
            "اكتب فقرة عن القرار التشغيلي الذي يخدمه النظام والنطاق الذي لا يغطيه النموذج.",
            "أضف Screenshot أو table preview يوضح شكل الجداول الأساسية.",
            "اشرح ماذا يمثّل الصف الواحد؟ في جدول stop_events بمثال صف واحد: رحلة، محطة، تحميل ركاب، وdelay.",
        ],
    },
    2: {
        "phase": "الجودة وKPIs",
        "label": "Week 2 - Quality and metrics",
        "summary": "يتعلم الطالب أن التحليل لا يبدأ قبل فحص البيانات، وأن كل KPI يجب أن يكون قابلا للتتبع إلى جدول وحقل وحساب.",
        "know": [
            "Quality Gate يعني أن النظام قد يمنع التحليل إذا كانت البيانات غير صالحة.",
            "الفرق بين critical issue وwarning، ولماذا لا تتساوى كل مشاكل البيانات.",
            "KPI الجيد له source table وfields وformula وthreshold وليس مجرد رقم في بطاقة.",
        ],
        "execute": [
            "تشغيل validate_dataset وقراءة passed وquality_score وfailed_checks.",
            "تشغيل analyze_dataset ومراجعة stop_summary وcause_summary وworst_trips.",
            "تتبع كل KPI من الواجهة إلى الحقول التي خرج منها في الجداول.",
        ],
        "test": [
            "تجربة حالة مرجعية مكسورة أو قيمة سالبة ومعرفة هل يتم إيقاف التحليل.",
            "مقارنة passed/failed counts قبل قبول النتائج.",
            "التأكد أن worst_stop لا يأتي من trips فقط بل من stop_events.",
        ],
        "report": [
            "اكتب ملخص Quality Gate: ماذا فحص؟ ماذا نجح؟ ماذا كان سيمنع التحليل؟",
            "أضف جدول KPI definitions يذكر source وformula وmeaning لكل مؤشر مهم.",
            "أرفق لقطة أو مخرج يثبت أن التحليل مبني على بيانات اجتازت الفحص.",
        ],
    },
    3: {
        "phase": "السيناريو والتوصية",
        "label": "Week 3 - Scenarios and recommendation",
        "summary": "ينتقل الطالب من وصف المشكلة إلى اختبار بدائل: ماذا يحدث لو غيرنا جزءا محددا من البيانات، وما الدليل وراء التوصية.",
        "know": [
            "baseline هو الوضع قبل التعديل، ولا يصح تغييره أثناء المقارنة.",
            "scenario ليس وعدا بأن المدينة ستتحسن فعليا؛ هو تجربة حسابية على افتراض واضح.",
            "recommendation المحترمة تجمع improvement وconfidence وfeasibility وlimitations.",
        ],
        "execute": [
            "تشغيل run_scenarios ومراجعة جدول المقارنة بين baseline وmodified.",
            "فتح أفضل scenario ومعرفة target_stop_id وexpected improvement.",
            "تشغيل build_recommendation وقراءة evidence وlimitations قبل الحكم على النتيجة.",
        ],
        "test": [
            "التأكد أن scenario لا يغير baseline الأصلي.",
            "مقارنة أثر scenario على محطة مستهدفة مقابل باقي المحطات.",
            "التأكد أن التوصية لا تظهر إذا فشل Quality Gate.",
        ],
        "report": [
            "أضف جدول scenario comparison يوضح التحسن المتوقع لكل بديل.",
            "اكتب لماذا تم اختيار البديل المقترح، وما القيود التي تمنع اعتباره قرارا نهائيا.",
            "أرفق evidence من stop_summary أو worst_trips يربط التوصية بمصدرها.",
        ],
    },
    4: {
        "phase": "التكامل والتقرير النهائي",
        "label": "Week 4 - Integration and final evidence",
        "summary": "يجمع الطالب كل الرحلة في pipeline واحد ويربط notebook مع Backend وFrontend وملفات الدليل التي تصلح للتقرير.",
        "know": [
            "run_full_pipeline يمثل ترتيب Backend: generate ثم validate ثم analyze ثم scenarios ثم recommendation.",
            "API لا يخترع النتائج؛ هو يعيد مخرجات pipeline للواجهة بصيغة قابلة للاستخدام.",
            "التقرير النهائي يحتاج أدلة: screenshots وCSV/JSON outputs واختبارات وشرح حدود النموذج.",
        ],
        "execute": [
            "تشغيل pipeline كاملا مع write_outputs=True لإنتاج ملفات evidence.",
            "فتح المخرجات النهائية ومقارنتها مع ما يظهر في واجهة DSS.",
            "تشغيل الاختبارات وربط كل اختبار بجزء من المنطق الذي يحميه.",
        ],
        "test": [
            "تشغيل pytest والتأكد أن pipeline وvalidation وAPI contract ما زالت تعمل.",
            "مقارنة Notebook output مع Backend response ومع واجهة المستخدم.",
            "التأكد أن التقرير لا يعتمد على Screenshot فقط بل على بيانات قابلة للمراجعة.",
        ],
        "report": [
            "اكتب workflow كامل من config إلى recommendation مع ذكر الملفات أو الصفحات التي تثبت كل خطوة.",
            "أرفق جدول evidence checklist: مصدر الدليل، أين يظهر، ولماذا يثبت إنجاز المهمة.",
            "اختم بتوصية مهنية وحدود النموذج والخطوات التالية الممكنة.",
        ],
    },
}


CELL_WEEK = {
    **{number: 1 for number in range(1, 14)},
    **{number: 2 for number in range(14, 19)},
    **{number: 3 for number in range(19, 23)},
    **{number: 4 for number in range(23, 28)},
}


CURATED_MARKDOWN = {
    1: {
        "title": "Bus Delay DSS - Jupyter Notebook",
        "paragraphs": [
            "هذه الصفحة تشرح notebook كرحلة هندسة برمجية كاملة. المشروع ليس عن النقل فقط؛ النقل هنا هو المثال التطبيقي الذي نستخدمه لفهم كيف يبنى نظام DSS من بيانات وقواعد وتحليل وواجهة.",
            "سيقرأ الطالب الكود على أنه pipeline: config يحدد الافتراضات، Python يحول الافتراضات إلى جداول، validation يمنع التحليل غير الآمن، analysis يحول الصفوف إلى KPIs، scenarios تختبر بدائل، وrecommendation تجمع الدليل في مخرج قابل للمراجعة.",
            "المهم ليس حفظ الكود. المهم أن يعرف الطالب لماذا توجد كل طبقة، ماذا يحدث لو تغيرت، وأين يظهر أثرها في الواجهة أو API.",
        ],
    },
    2: {
        "title": "1. خريطة رحلة Jupyter Notebook",
        "paragraphs": [
            "سنقرأ notebook بترتيب التنفيذ وليس بترتيب الحفظ. كل جزء يعتمد على السابق: لا معنى لـ KPI قبل فهم شكل الصف، ولا معنى لـ recommendation قبل quality gate، ولا معنى لـ scenario قبل baseline.",
            "إذا شعر الطالب أن الكود طويل، فليقرأه كسلسلة صغيرة: تعريف القرار، تعريف القواعد، توليد الجداول، فحص الجداول، حساب المؤشرات، تجربة السيناريوهات، ثم بناء التوصية.",
        ],
        "bullets": [
            "Project context: تحديد القرار والنطاق قبل الكود.",
            "Config: نقل الافتراضات إلى قيم قابلة للتعديل.",
            "Dataset generation: بناء جداول مترابطة وليست أرقاما عشوائية.",
            "Quality gate: منع التحليل إذا كانت البيانات غير صالحة.",
            "KPIs: تحويل الصفوف إلى إشارات تساعد الواجهة.",
            "Scenario Lab: مقارنة baseline مع modified data.",
            "Recommendation: إخراج قرار مشروط بالدليل والقيود.",
        ],
    },
    4: {
        "title": "2. سياق المشروع: ما القرار الذي يخدمه النظام؟",
        "paragraphs": [
            "قبل كتابة أي كود يجب أن نعرف ما القرار الذي سيخدمه النظام. في هذا المثال، لا نريد فقط أن نقول إن Route B12 يتأخر. هذا وصف عام لا يساعد فريق التشغيل كثيرا.",
            "السؤال العملي هو: ما أول تدخل تشغيلي يستحق التجربة على Route B12 بناء على الدليل؟ هل نبدأ بتنظيم الصعود في محطة محددة؟ هل نعدل الجدولة؟ هل نحتاج حافلة إضافية؟ كل خيار له أثر وتكلفة وثقة مختلفة.",
            "لذلك يجب أن ينتج النظام أدلة قابلة للتتبع: أين يظهر التأخير؟ هل البيانات اجتازت الفحص؟ ما الوضع الحالي baseline؟ ماذا تغير عند تجربة كل scenario؟ وما حدود الثقة في التوصية؟",
            "بهذا الشكل يصبح DSS أداة تساعد على مراجعة قرار، لا مجرد Dashboard يعرض أرقاما جميلة.",
        ],
    },
    6: {
        "title": "3. Config: أين نضع الافتراضات؟",
        "paragraphs": [
            "في المشاريع الجيدة لا ندفن الافتراضات داخل الدوال. إذا كانت سعة الحافلة أو عدد الرحلات أو ساعات الذروة مكتوبة داخل function بشكل ثابت، سيصعب على الطالب أو الفريق تغيير التجربة وفهم أثر التغيير.",
            "لذلك نستخدم config. الconfig هنا ليس ملف إعدادات شكلي؛ هو طريقة لفصل السؤال عن طريقة الحساب. عندما نغير trip_count أو peak_hours أو saving_factor نغير التجربة نفسها، بينما تبقى الدوال العامة كما هي.",
            "هذا يعلم الطالب مبدأ مهما في تطوير البرمجيات: الكود الجيد لا يجبرك على فتح function كل مرة تريد تغيير assumption. يجعل الأشياء المتغيرة واضحة وقابلة للمراجعة.",
        ],
    },
    8: {
        "title": "4. توليد البيانات: من قواعد إلى جداول",
        "paragraphs": [
            "هذه المرحلة تحول config إلى dataset. لا نريد أرقاما مبعثرة، بل جداول لها علاقات واضحة. هذا هو الفرق بين demo ضعيف وDSS يمكن شرحه.",
            "routes يصف المسار. stops يصف المحطات وترتيبها. trips يصف الرحلات. stop_events يصف وصول كل رحلة إلى كل محطة. هذا الجدول الأخير هو الأغنى لأنه يحمل الحمل، مدة الوقوف، سبب التأخير، والتأخير المتراكم.",
            "إذا فهم الطالب stop_events، سيفهم معظم النظام. كل Dashboard أو Explorer أو Scenario لاحقا يعود في النهاية إلى صفوف من هذا الجدول.",
        ],
    },
    10: {
        "title": "5. فحص الجداول قبل الحساب",
        "paragraphs": [
            "قبل بناء أي KPI يجب فتح الجداول. هذه خطوة بسيطة لكنها تمنع أخطاء كبيرة. الطالب يجب أن يسأل: ماذا يمثل الصف الواحد؟ هل هذا جدول رحلات أم جدول أحداث داخل الرحلة؟",
            "عند رؤية stop_events مثلا، يجب أن يلاحظ أن trip_id يتكرر لأن الرحلة تمر على عدة محطات، وأن stop_id يتكرر لأن المحطة تظهر في رحلات متعددة. هذا التكرار ليس خطأ؛ هو نتيجة مباشرة لسؤال: ماذا يمثّل الصف الواحد؟",
            "إذا لم يفهم الطالب ماذا يمثّل الصف الواحد؟ سيخلط بين عدد الرحلات وعدد أحداث المحطات، وقد يحسب KPI يبدو صحيحا لكنه مبني على مستوى صف خاطئ.",
        ],
    },
    12: {
        "title": "6. Data model والعلاقات",
        "paragraphs": [
            "Data model يشرح كيف تتصل الجداول. العلاقات هنا ليست رسما نظريا؛ هي التي تسمح للواجهة أن تفتح trip ثم ترى محطاته، أو تفتح stop ثم ترى الرحلات التي مرت عليه.",
            "العلاقة routes to trips تعني أن المسار يحتوي رحلات. العلاقة routes to stops تعني أن المسار يحتوي محطات. أما stop_events فهو نقطة الالتقاء بين trips وstops.",
            "هذا يشرح لماذا نحتاج foreign keys. إذا كان stop_event يشير إلى trip غير موجودة، فلن يستطيع النظام شرح التأخير. وإذا كان يشير إلى stop غير موجودة، فلن نستطيع تحديد موقع المشكلة.",
        ],
    },
    14: {
        "title": "7. Quality Gate: لماذا نوقف التحليل أحيانا؟",
        "paragraphs": [
            "Quality Gate ليس رسالة نجاح أو فشل فقط. هو قرار برمجي: هل يسمح النظام للبيانات أن تتحول إلى تحليل وتوصية؟",
            "في DSS، الخطأ الخطير ليس فقط أن يفشل الكود. الخطأ الأخطر أن ينجح الكود ويعرض recommendation مبنية على بيانات مكسورة. لذلك validation جزء من أخلاقيات النظام وليس خطوة تقنية جانبية.",
            "الفحوص هنا تعلم الطالب أن البيانات لها شروط: الجداول يجب أن توجد، العلاقات يجب أن تكون صحيحة، القيم لا يجب أن تكون سالبة، وتسلسل المحطات يجب أن يكون منطقيا.",
        ],
    },
    16: {
        "title": "8. KPI calculation: كيف يتحول الصف إلى مؤشر؟",
        "paragraphs": [
            "KPI ليس اسما على بطاقة. هو سؤال تشغيلي يتحول إلى formula. إذا لم نعرف source table وfields وthreshold، يصبح KPI مجرد رقم بلا معنى.",
            "on_time_rate يعتمد على trips لأن السؤال عن الرحلة كاملة. أما worst_stop فيعتمد على stop_events لأن السؤال عن مكان تراكم التأخير داخل المسار.",
            "هذه التفرقة مهمة للطلاب: ليس كل مؤشر يحسب من نفس الجدول. اختيار الجدول الصحيح جزء من التفكير البرمجي والتحليلي.",
        ],
    },
    19: {
        "title": "9. Scenario Lab: تجربة تغيير قبل التوصية",
        "paragraphs": [
            "Scenario Lab لا يقول ماذا سيحدث فعليا في المدينة. هو يقول: إذا افترضنا تدخلا محددا، كيف يمكن أن تتغير الأرقام داخل dataset؟",
            "هذا مهم لأن القرار لا يبنى على worst_stop فقط. قد تكون المحطة واضحة، لكن نوع التدخل يحتاج مقارنة. تنظيم الصعود، تعديل الجدولة، أو إضافة حافلة كلها تغير البيانات بطرق مختلفة.",
            "السيناريو الجيد يترك baseline محفوظا، يغير نسخة من البيانات، يعيد حساب KPIs، ثم يقارن. بدون هذه الخطوات تصبح المقارنة كلاما لا تجربة.",
        ],
    },
    21: {
        "title": "10. Recommendation logic: كيف تصبح النتيجة قابلة للمراجعة؟",
        "paragraphs": [
            "Recommendation ليست جملة مثل نفذوا الحل الفلاني. في النظام الجيد، التوصية هي object يحتوي action وtarget وconfidence وevidence وlimitations وnext_step.",
            "أول شرط هو السلامة: إذا فشلت Quality Gate لا تظهر recommendation. هذا يحمي المستخدم من قرار يبدو ذكيا لكنه مبني على بيانات غير صالحة.",
            "بعد ذلك يتم اختيار أفضل scenario بناء على action_score، لكن النتيجة لا تقدم كحقيقة نهائية. هي اقتراح للتجربة والمراجعة مع توضيح القيود.",
        ],
    },
    23: {
        "title": "11. Full pipeline: ترتيب التشغيل",
        "paragraphs": [
            "بعد فهم الدوال منفصلة، نحتاج دالة واحدة تجمع الرحلة. هذا هو دور run_full_pipeline. هي تمنع الفوضى وتجعل Backend يعرف الترتيب الصحيح.",
            "الترتيب هنا مهم جدا: generate ثم validate ثم analyze ثم scenarios ثم recommendation. إذا اختصر الطالب هذه السلسلة أو غير ترتيبها، سيتغير معنى النظام.",
            "عند تشغيل pipeline مع write_outputs، يتحول العمل إلى ملفات دليل: CSV وJSON يمكن فتحها وفحصها ومقارنتها مع الواجهة.",
        ],
    },
    25: {
        "title": "12. ماذا يجب أن يفهم الطالب بعد القراءة؟",
        "paragraphs": [
            "هذه ليست أسئلة اختبار في النقل. هي نقاط فهم تقنية: هل يستطيع الطالب ربط الكود بالبيانات والواجهة؟ هل يعرف أين يعيش كل جزء؟ هل يعرف لماذا يمنع النظام recommendation عند فشل الجودة؟",
            "إذا استطاع الطالب تتبع stop_events من generator إلى analysis إلى Explorer، فقد فهم العمود الفقري للمشروع. وإذا استطاع شرح كيف يغير scenario البيانات ثم يعيد حساب KPIs، فقد فهم معنى DSS عملي.",
        ],
    },
    27: {
        "title": "13. ربط Jupyter Notebook بملفات repo",
        "paragraphs": [
            "Jupyter Notebook هو مسار التعلم. أما repo فهو المنتج المنظم. لذلك يجب أن يعرف الطالب أين ينتقل بعد فهم كل خلية.",
            "الكود الذي ظهر في notebook يعيش في ملفات Backend مثل generator.py وvalidation.py وanalysis.py وscenarios.py وrecommendation.py وpipeline.py. الواجهة تقرأ هذه النتائج عبر API وتعرضها في صفحات DSS.",
        ],
    },
}


CELL_EXPLANATIONS = {
    3: [
        "هذه الخلية تجهز بيئة العمل. وجود imports في البداية يجعل notebook self-contained: الطالب لا يحتاج أن يعرف كل ملفات Backend قبل أن يفهم الرحلة.",
        "استخدام pandas مهم هنا لأن معظم العمل التعليمي يعتمد على DataFrames. كل جدول في المشروع، مثل routes أو stop_events، يقرأ كجدول بيانات يمكن فحصه وتجميعه وتحويله إلى JSON لاحقا.",
        "السطر الخاص بـ display ليس زينة. في Jupyter، display يعرض الجداول بطريقة أوضح من print. أما إذا شغل الطالب الكود خارج Jupyter، فهناك fallback بسيط حتى لا يفشل التنفيذ فقط بسبب غياب display.",
    ],
    5: [
        "هذه الخلية تضع project context. هذا مهم جدا لأن DSS لا يبدأ من جدول بيانات فقط؛ يبدأ من قرار يحتاج دعما. هنا القرار هو اختيار أول intervention يستحق التجربة على Route B12.",
        "وجود scope يساعد الطلاب على عدم توسيع المشروع بلا حدود. included يحدد ما سيدعمه النموذج التعليمي، وexcluded يوضح ما لا يدعي النظام حله مثل live AVL أو قرار procurement أو تحسين الشبكة بالكامل.",
        "الافتراضات assumptions ليست كلاما جانبيا. هي جزء من سلامة النظام: Synthetic Data يجب أن توسم بوضوح، وRecommendation لا يجب أن تظهر إلا بعد اجتياز Data Quality.",
    ],
    7: [
        "هذه الخلية تعلم الطالب كيف يفصل بين منطق البرنامج وبين الافتراضات القابلة للتغيير. في مشروع حقيقي، لا نريد أن يفتح المطور دالة التحليل كل مرة يريد تغيير عدد الرحلات أو حد الالتزام بالوقت أو شدة المشكلة في محطة معينة.",
        "generation_rules هو وصف للعالم التجريبي الذي سنبني عليه البيانات. seed يجعل النتائج قابلة للتكرار. trip_count يحدد حجم العينة. bus_capacity يدخل في فحص الجودة. stops لا تعني أسماء محطات فقط؛ كل stop يحمل base_boarding وproblem_weight، أي أن المحطة نفسها لها سلوك متوقع ومخاطر مختلفة.",
        "delay_causes يشرح كيف تتحول الأسباب إلى أثر رقمي. boarding وtraffic وschedule_gap ليست labels للعرض فقط؛ لكل سبب base_seconds وvariability. هذا يعني أن سبب التأخير سيؤثر على dwell_time_sec وadded_delay_sec، ثم سيظهر لاحقا في cause_summary.",
        "kpi_config يحدد معنى المؤشر قبل حسابه. on_time_threshold_sec مثلا يقرر متى نعتبر الرحلة ملتزمة بالوقت. إذا تغير threshold من 300 إلى 180 ثانية، ستتغير on_time_rate حتى لو بقيت البيانات نفسها. هذا درس مهم: بعض النتائج تتغير بسبب تعريف المؤشر وليس بسبب تغير الواقع.",
        "scenarios_config يحول فكرة التدخل إلى قيم قابلة للحساب. target_stop_id يحدد الصفوف المتأثرة، saving_factor يحدد مقدار التحسن المفترض، cost_factor يمثل تكلفة أو صعوبة التدخل، وfeasibility يمثل سهولة التنفيذ. هذه القيم ستدخل لاحقا في action_score، لذلك يجب قراءتها كجزء من منطق القرار لا كإعدادات شكلية.",
    ],
    9: [
        "هذه الخلية تولد data model كامل. ليس المقصود إنتاج أرقام كثيرة، بل إنتاج جداول مترابطة يمكن أن تشبه بنية نظام DSS حقيقي.",
        "routes يمثل تعريف المسار وسعة الحافلة. stops يمثل المحطات بالترتيب. trips يمثل الرحلات المجدولة. stop_events هو أهم جدول لأنه يربط trip مع stop ويضع عليه load وdwell وdelay cause وcumulative delay.",
        "داخل الحلقة، كل trip تمر على كل stop. هذا يجيب عن سؤال ماذا يمثّل الصف الواحد؟ الصف في stop_events يعني حافلة وصلت إلى محطة معينة أثناء رحلة معينة. إذا ضاع هذا المعنى، تصبح كل الرسومات والتحليلات لاحقا غير مفهومة.",
        "الدوال الصغيرة choose_delay_cause وcause_delay_seconds تجعل منطق التأخير قابل للفهم. المشكلة ليست random فقط؛ المشكلة تتأثر بـ problem_weight وبوقت الذروة is_peak وبنوع السبب.",
    ],
    11: [
        "هذه الخلية لا تحسب شيئا جديدا، لكنها من أهم الخلايا تعليميا. قبل أي KPI يجب فتح الجداول ومشاهدة شكل الصفوف.",
        "عندما يرى الطالب routes وstops وtrips وstop_events، يبدأ بفهم الفرق بين table-level summary وrow-level evidence. Dashboard لاحقا يلخص، لكن الدليل الحقيقي موجود في الصفوف.",
        "هذه المعاينة تساعد الطالب على كشف أخطاء مبكرة: هل stop_id واضح؟ هل trip_id متكرر بطريقة منطقية؟ هل added_delay_sec موجود؟ هل delay_cause مفهوم؟",
    ],
    13: [
        "هذه الخلية تحول العلاقات إلى جدول تعليمي. الطالب يحتاج أن يرى schema قبل أن يرى ERD أو API response.",
        "الفكرة الأساسية: routes يرتبط بـ trips وstops، ثم trips وstops يلتقيان داخل stop_events. لذلك stop_events ليس جدول إضافي عشوائي؛ هو جدول الأحداث الذي يسمح بتحليل التأخير على مستوى المحطة والرحلة.",
    ],
    15: [
        "هذه الخلية تشرح Quality Gate. في DSS محترم، لا ننتقل من البيانات إلى recommendation مباشرة. يجب أولا أن نسأل: هل البيانات صالحة للتحليل؟",
        "required_tables يحمي من نقص الجداول. valid_trip_references وvalid_stop_references يحميان العلاقات. non_negative_time يحمي من قيم غير منطقية. capacity_not_exceeded يعطي warning لأن تجاوز السعة قد يكون خطأ أو assumption يحتاج مراجعة.",
        "النتيجة ليست فقط passed true أو false. الطالب يجب أن يقرأ quality_score وfailed_checks وseverity. الفرق بين critical وwarning مهم: critical يمكن أن يمنع analysis، بينما warning قد يسمح بالتحليل مع توضيح محدودية.",
    ],
    17: [
        "هذه الخلية تحول البيانات إلى KPIs. يجب أن يفهم الطالب أن KPI ليس بطاقة جميلة في الواجهة، بل حساب له source table وfields وformula وthreshold وحدود.",
        "on_time_rate يحسب نسبة الرحلات التي final_delay_sec لديها أقل أو يساوي threshold. avg_final_delay_sec يلخص التأخير النهائي للرحلات. avg_dwell_time_sec يوضح سلوك الوقوف والصعود. worst_stop يحدد أين يظهر التأخير المضاف بشكل أكبر.",
        "stop_summary يستخدم groupby على stop_id وstop_name. هذا يعني أن التحليل ينتقل من row-level events إلى stop-level ranking. cause_summary يستخدم groupby على delay_cause لمعرفة أي سبب ينتج أكبر مجموع تأخير.",
    ],
    18: [
        "هذه الخلية تعرض مخرجات التحليل كجداول. هذا مهم لأن الطالب يجب أن يرى نفس النتيجة قبل أن تتحول إلى cards أو charts في الواجهة.",
        "Stop ranking يجيب: أين تتراكم المشكلة؟ Delay cause summary يجيب: ما نوع السبب الأكثر تكلفة؟ Worst trips يجيب: أي رحلات يجب فتحها إذا أردنا فحص أمثلة ملموسة؟",
    ],
    20: [
        "هذه الخلية تشرح Scenario Lab. السيناريو ليس توقعا مؤكدا وليس توصية نهائية. هو تجربة حسابية تقول: إذا غيرنا جزءا محددا في البيانات، كيف يتغير baseline؟",
        "run_scenarios يبدأ من baseline KPIs، ثم يطبق كل scenario على نسخة من stop_events. هذا مهم: لا نعدل baseline نفسه، لأن المقارنة ستصبح غير عادلة.",
        "apply_scenario يقلل delay في target_stop_id بناء على saving_factor. بعدها يتم تحديث cumulative_delay_sec لأن التأخير يتراكم على طول الرحلة. ثم recalculate_trips يعيد بناء final_delay_sec من آخر stop_event في كل trip.",
        "action_score ليس حقيقة مطلقة. هو ranking تعليمي يجمع improvement وfeasibility وconfidence ويقسم على cost_factor. لذلك قد يكون scenario يحسن كثيرا لكن ترتيبه أقل إذا كان مكلفا أو صعب التنفيذ.",
    ],
    22: [
        "هذه الخلية تبني recommendation. الفرق بين Dashboard وDSS يظهر هنا: Dashboard يعرض مؤشرات، أما DSS فينتج مخرجا قابلا للمراجعة مع evidence وlimitations.",
        "أول شرط في الدالة هو quality gate. إذا فشلت الجودة، لا توجد توصية. هذا يعلم الطالب أن النظام الآمن يعرف متى يتوقف.",
        "إذا كانت البيانات كافية والجودة ناجحة، تختار الدالة أفضل scenario وتعيد recommended_action وtarget_stop_id وexpected_improvement_sec وconfidence وaction_score.",
        "limitations جزء أساسي من المخرج. عندما نقول Synthetic training data أو No live AVL feed فنحن لا نضعف المشروع؛ نحن نجعل التوصية مهنية وقابلة للمراجعة.",
    ],
    24: [
        "هذه الخلية تجمع الرحلة في run_full_pipeline. هذه هي طريقة التفكير في Backend: لا نريد أن يضغط المستخدم أزرارا كثيرة لكي يتذكر ترتيب التشغيل.",
        "الترتيب مهم: generate ثم validate ثم analyze ثم scenarios ثم recommendation. إذا تغير هذا الترتيب قد تظهر recommendation قبل التأكد من جودة البيانات.",
        "عند write_outputs=True، تكتب الدالة ملفات evidence مثل CSV وJSON. هذه الملفات تساعد الطالب على تقديم دليل ملموس: ليس فقط Screenshot من الواجهة، بل مخرجات بيانات قابلة للفتح والمراجعة.",
    ],
    26: [
        "هذه الخلية تصنع summary نهائي. الملخص لا يحل محل التفاصيل، لكنه يساعد على عرض النتيجة بسرعة: ما المشروع؟ كم جدول؟ ما quality_score؟ ما أفضل scenario؟ وما التوصية؟",
        "هذا النوع من الملخص مفيد في نهاية demo لأن الطالب يستطيع الرجوع منه إلى أي جزء تفصيلي: البيانات، الجودة، التحليل، السيناريو، أو recommendation.",
    ],
}


FUNCTION_DETAILS = {
    "display": {
        "file": "notebooks/bus_delay_full_journey_expanded.ipynb",
        "title": "عرض الجداول داخل Jupyter أو خارجه",
        "paragraphs": [
            "هذه دالة fallback صغيرة. في Jupyter توجد display عادة بشكل جاهز وتعرض DataFrames بطريقة مرئية. لكن إذا شغل الطالب الكود في Python عادي، قد لا تكون display موجودة.",
            "بدلا من أن يفشل notebook بسبب أداة عرض فقط، يعرّف الكود نسخة بسيطة تستخدم print. هذا مثال صغير على defensive coding: نجعل تجربة التعلم تعمل في أكثر من بيئة.",
        ],
        "example": "داخل Jupyter سيظهر جدول pandas بشكل منسق. خارج Jupyter سيطبع المحتوى نصيا بدلا من إيقاف التنفيذ.",
    },
    "generate_dataset": {
        "file": "backend/generator.py",
        "title": "توليد dataset مترابط",
        "paragraphs": [
            "هذه الدالة هي مصنع البيانات في المشروع. هي لا تنشئ جدولا واحدا فقط، بل تنشئ أربعة جداول لها علاقة واضحة ببعضها. هذا يعلّم الطالب أن التطبيق الذكي لا يبدأ من chart؛ يبدأ من data model يمكن تتبعه.",
            "المدخل الأساسي هو rules. هذا يعني أن سلوك الدالة قابل للتعديل من config: عدد الرحلات، المحطات، وزن المشكلة في كل محطة، ساعات الذروة، وسعة الحافلة. عندما يعدل الطالب config فهو يغير العالم الافتراضي الذي يختبره النظام.",
            "المخرج هو dictionary يحتوي DataFrames. هذا مناسب تعليميا لأن الطالب يرى كل جدول منفصلا، ومناسب برمجيا لأن Backend يستطيع تمرير نفس الجداول إلى validation وanalysis وscenarios.",
        ],
        "example": "إذا زاد problem_weight في S03، ستختار الدالة أسباب تأخير أكبر في هذه المحطة، ثم يظهر ذلك لاحقا في worst_stop وstop_summary.",
    },
    "choose_delay_cause": {
        "file": "backend/generator.py",
        "title": "اختيار سبب التأخير",
        "paragraphs": [
            "هذه الدالة الصغيرة تمنع البيانات من أن تكون random بلا معنى. هي تستخدم problem_weight وis_peak لزيادة احتمال أسباب معينة.",
            "في ساعة الذروة، traffic يصبح أكثر احتمالا. في محطة ذات problem_weight مرتفع، boarding يصبح أكثر حضورا. هذا يجعل البيانات synthetic لكنها ليست عبثية.",
        ],
        "example": "Central Hospital لها problem_weight أعلى، لذلك يظهر boarding أكثر، وهذا يجعل Organized Boarding سيناريو منطقيا للاختبار.",
    },
    "cause_delay_seconds": {
        "file": "backend/generator.py",
        "title": "تحويل السبب إلى ثواني تأخير",
        "paragraphs": [
            "بعد اختيار السبب، يجب تحويله إلى أثر رقمي. هذه الدالة تستخدم base_seconds وvariability ثم تضيف ضغط المشكلة وساعة الذروة.",
            "هذا الربط مهم: السبب النصي delay_cause وحده لا يكفي. DSS يحتاج رقما يمكن جمعه ومقارنته وتحويله إلى KPI.",
        ],
        "example": "traffic في peak hour يعطي عادة added_delay أعلى من schedule_gap خارج الذروة.",
    },
    "validate_dataset": {
        "file": "backend/validation.py",
        "title": "فحص جودة البيانات قبل التحليل",
        "paragraphs": [
            "هذه الدالة هي gate. لا يجوز أن ينتقل النظام إلى KPIs وrecommendation إذا كانت العلاقات أو القيم الأساسية مكسورة.",
            "هي تفحص وجود الجداول، صحة trip_id وstop_id، عدم وجود قيم سالبة، عدم تجاوز الحمل لسعة الحافلة، وترتيب المحطات داخل الرحلة.",
            "القيمة التعليمية هنا أن الطالب يرى الفرق بين خطأ يمنع التحليل critical وبين warning يحتاج توضيحا. ليس كل مشكلة لها نفس الخطورة.",
        ],
        "example": "إذا ظهر stop_event يشير إلى stop_id غير موجود، فإن Stop View في Explorer لا يستطيع تفسير موقع التأخير بشكل موثوق.",
    },
    "check": {
        "file": "backend/validation.py",
        "title": "توحيد شكل نتيجة الفحص",
        "paragraphs": [
            "هذه helper تجعل كل فحص يرجع بنفس البنية: id وpassed وseverity وmessage. هذا يسهل على الواجهة عرض النتائج بدون معرفة تفاصيل كل فحص.",
            "وجود شكل ثابت للنتيجة هو API contract مصغر. إذا احترم Backend هذا العقد، تستطيع الواجهة عرض quality checks بوضوح.",
        ],
        "example": "required_tables وnon_negative_time يرجعان نفس الشكل رغم أن منطق الفحص مختلف.",
    },
    "records": {
        "file": "backend/analysis.py",
        "title": "تحويل DataFrame إلى JSON",
        "paragraphs": [
            "pandas DataFrame ممتاز للتحليل، لكنه ليس شكل الاستجابة الذي تستهلكه React بسهولة. هذه helper تحول الصفوف إلى list of dictionaries.",
            "round(2) يجعل الأرقام أكثر قراءة في الواجهة. الطالب يرى هنا أن تجهيز البيانات للواجهة جزء من هندسة النظام وليس مجرد تنسيق.",
        ],
        "example": "stop_summary بعد groupby يتحول إلى rows يمكن للواجهة رسمها في ranking أو table.",
    },
    "analyze_dataset": {
        "file": "backend/analysis.py",
        "title": "حساب KPIs والدليل",
        "paragraphs": [
            "هذه الدالة هي مركز التحليل. تقرأ trips وstop_events وتحولها إلى مؤشرات ومجاميع مفهومة.",
            "on_time_rate يعتمد على final_delay_sec في trips. stop_summary يعتمد على stop_events لأننا نريد ترتيب المحطات حسب التأخير المضاف. cause_summary يعتمد على delay_cause لمعرفة السبب الأكثر تأثيرا.",
            "النتيجة لا تخدم صفحة واحدة فقط. نفس output يستخدم في Dashboard وDelay Evidence وRecommendation. لذلك أي خطأ هنا ينتشر في المنتج كله.",
        ],
        "example": "إذا كان worst_stop هو S03، فهذا لا يعني القرار النهائي، لكنه يحدد أين يبدأ التفتيش وأي scenario يستحق التجربة.",
    },
    "run_scenarios": {
        "file": "backend/scenarios.py",
        "title": "مقارنة سيناريوهات what-if",
        "paragraphs": [
            "هذه الدالة تقارن مجموعة interventions. تبدأ من baseline ثم تطبق كل scenario على نسخة معدلة من البيانات.",
            "بعد تعديل البيانات، تعيد حساب KPIs. هذا مهم لأن scenario لا يجب أن يغير card في الواجهة فقط؛ يجب أن يغير underlying data ثم يعيد بناء المؤشر.",
            "ranking يعتمد على improvement وconfidence وfeasibility وcost_factor. هذا يعلم الطالب أن أفضل قرار ليس دائما أكبر تحسن رقمي.",
        ],
        "example": "Additional Bus قد يوفر زمنا أكبر، لكن cost_factor العالي وfeasibility الأقل قد يخفضان action_score.",
    },
    "apply_scenario": {
        "file": "backend/scenarios.py",
        "title": "تطبيق التدخل على صفوف محددة",
        "paragraphs": [
            "هذه الدالة هي المكان الذي يتحول فيه scenario من فكرة إلى تعديل بيانات. تستخدم target_stop_id لتحديد الصفوف المتأثرة.",
            "بعد حساب saving، يتم تقليل dwell_time_sec وadded_delay_sec ثم إعادة cumulative_delay_sec. هذا يمنع ظهور تحسن في محطة واحدة دون أن ينعكس على بقية الرحلة.",
        ],
        "example": "Organized Boarding على S03 يقلل issue_wait_sec في صفوف S03، ثم يتغير final_delay_sec عند نهاية كل trip.",
    },
    "recalculate_trips": {
        "file": "backend/scenarios.py",
        "title": "إعادة حساب تأخير الرحلة النهائي",
        "paragraphs": [
            "بعد تعديل stop_events، جدول trips يصبح قديما إذا لم نحدث final_delay_sec. هذه الدالة تأخذ آخر stop_event في كل trip وتستخدم cumulative_delay_sec كقيمة نهائية.",
            "هذا يعلّم الطالب أن الجداول المشتقة يجب أن يعاد حسابها بعد أي scenario. لا يكفي تعديل جدول واحد وترك الباقي كما هو.",
        ],
        "example": "إذا انخفض cumulative_delay_sec في S05 بعد scenario، يجب أن ينخفض final_delay_sec في trips.",
    },
    "confidence_score": {
        "file": "backend/scenarios.py",
        "title": "حساب ثقة مبسطة للتعليم",
        "paragraphs": [
            "هذه الدالة ليست نموذج AI حقيقي. هي formula تعليمية تشرح كيف يمكن أن تدخل feasibility وcost_factor وimprovement في إشارة ثقة.",
            "المهم أن الطالب يفهم أن confidence ليست شعورا. هي قيمة يجب أن تكون مبنية على قواعد أو نموذج أو دليل.",
        ],
        "example": "سيناريو feasible ورخيص وله improvement واضح يحصل على confidence أعلى من سيناريو مكلف وصعب التنفيذ.",
    },
    "generate_recommendation": {
        "file": "backend/recommendation.py",
        "title": "إنتاج recommendation قابلة للمراجعة",
        "paragraphs": [
            "هذه الدالة تجمع كل الرحلة في مخرج واحد. تبدأ بالسؤال الآمن: هل فشلت quality gate؟ إذا نعم، يتم إيقاف التوصية.",
            "إذا نجحت الجودة، تختار أفضل scenario وتضيف evidence: quality_score وworst_stop وbaseline وscenario result. لذلك يستطيع المستخدم الرجوع من التوصية إلى البيانات التي دعمتها.",
            "limitations ليست إضافة شكلية. هي جزء من المهنية: Synthetic Data، عدم وجود live feed، وتبسيط التكلفة كلها حدود يجب أن تظهر قبل اتخاذ أي قرار حقيقي.",
        ],
        "example": "recommended_action = Organized Boarding لا تعني التنفيذ الفوري، بل تعني: هذا أفضل تدخل أولي للتجربة والمراجعة بناء على البيانات الحالية.",
    },
    "run_full_pipeline": {
        "file": "backend/pipeline.py",
        "title": "تشغيل الرحلة كاملة",
        "paragraphs": [
            "هذه الدالة تجعل النظام قابلا للتشغيل من نقطة واحدة. بدلا من أن يتذكر الطالب ترتيب كل دالة، pipeline يفرض الترتيب الصحيح.",
            "هذا الترتيب يحمي المعنى: لا analysis قبل generation، لا recommendation قبل validation، ولا scenario ranking قبل إعادة حساب KPIs.",
            "عند write_outputs=True، يتحول التشغيل إلى evidence files. هذه الملفات مهمة للتدريب لأنها تثبت أن النتائج جاءت من pipeline وليس من نص مكتوب يدويا.",
        ],
        "example": "FastAPI endpoints يمكنها استدعاء run_full_pipeline ثم اختيار جزء من النتيجة: data-quality أو kpis أو scenarios أو recommendation.",
    },
}


OUTPUTS = {
    3: ("Environment ready", "تم تجهيز بيئة notebook. هذا لا ينتج قرارا، لكنه يجعل الخلايا التالية قابلة للتنفيذ والفحص.", "pandas display.max_columns = 40\npandas display.width = 140"),
    5: ("Project context", "المخرج المتوقع هو dictionary يوضح القرار والنطاق والافتراضات. هذه هي نقطة البداية الصحيحة لأي DSS.", "project_name: Bus Delay DSS\nroute_id: B12\ndecision_owner: Public Transport Operations Manager\ndecision_to_support: Select the first operational intervention to test on route B12"),
    7: ("Config loaded", "هذه القيم ستؤثر في كل شيء لاحقا: شكل البيانات، معنى on-time، الفحوص، والسيناريوهات.", "trip_count: 36\nbus_capacity: 60\nproblem stop: S03 Central Hospital\non_time_threshold_sec: 300\npassing_score: 0.85\nscenarios: Organized Boarding, Ticket Machine, Additional Bus, Schedule Adjustment"),
    9: ("Generated dataset", "النتيجة هي data model مصغر. أهم نقطة: stop_events يحتوي الصفوف التي ستشرح التأخير لاحقا.", "routes: 1 row\nstops: 5 rows\ntrips: 36 rows\nstop_events: 180 rows"),
    11: ("Table preview", "المعاينة المتوقعة تجعل الطالب يرى الفرق بين route وtrip وstop_event قبل حساب أي رقم.", "routes\nB12 | North Station to Civic Center | capacity 60\n\nstops\nS01 North Station\nS02 Market Street\nS03 Central Hospital\nS04 University Gate\nS05 Civic Center\n\nstop_events sample\nT001 | S03 | passenger_load 48 | added_delay_sec 104 | delay_cause boarding"),
    13: ("Data model summary", "هذا المخرج يختصر العلاقات والمفاتيح، ويمهد لفهم ERD وصفحة Data Model.", "routes(route_id) -> trips(route_id)\nroutes(route_id) -> stops(route_id)\ntrips(trip_id) -> stop_events(trip_id)\nstops(stop_id) -> stop_events(stop_id)"),
    15: ("Validation report", "هذه النتيجة تحدد هل التحليل مسموح. عند فشل critical checks يجب أن يتوقف DSS قبل recommendation.", "quality_score: 1.0\nanalysis_gate: allowed\npassed_checks: 6\nfailed_checks_count: 0\nfailed_checks: []"),
    17: ("KPI result", "هذه القيم هي مادة Dashboard وExplorer. كل رقم يجب أن يعود إلى جدول وحقل وحساب.", "trips_analyzed: 36\non_time_rate: 0.28\navg_final_delay_sec: 1142.1\navg_dwell_time_sec: 70.4\nworst_stop: Central Hospital\nworst_stop_id: S03"),
    18: ("Analysis tables", "هذه الجداول تعرض التحليل من ثلاث زوايا: المحطات، الأسباب، والرحلات الأسوأ.", "Stop ranking: S03 Central Hospital highest average added delay\nCause summary: boarding highest total added delay\nWorst trips: peak-hour trips appear near the top"),
    20: ("Scenario results", "السيناريوهات تقارن baseline مع modified data. النتيجة ليست وعدا بل دليل أولي للتجربة.", "Organized Boarding: improvement 148.5s | confidence 0.79 | action_score 88.2\nTicket Machine: improvement 121.3s | confidence 0.72 | action_score 34.1\nAdditional Bus: improvement 176.2s | confidence 0.71 | action_score 26.4"),
    22: ("Recommendation", "المخرج النهائي يحتوي التوصية والدليل والقيود. هذا هو الفرق بين chart وبين DSS.", "status: recommendation_ready\nrecommended_action: Organized Boarding\ntarget_stop_id: S03\nexpected_improvement_sec: 148.5\nnext_step: Run a controlled pilot and compare before/after KPIs"),
    24: ("Pipeline object", "الدالة ترجع كل ما تحتاجه API والواجهة، ويمكنها كتابة ملفات evidence عند الحاجة.", "result keys:\nproject\ndataset\nvalidation\nanalysis\nscenarios\nrecommendation\n\noutput files:\nroutes.csv, stops.csv, trips.csv, stop_events.csv\nvalidation_report.json, analysis_summary.json, scenario_results.json"),
    26: ("Final summary", "هذا ملخص مناسب لنهاية تشغيل notebook، لكنه لا يلغي قراءة التفاصيل.", "project: Bus Delay DSS\nroute: B12\nquality_score: 1.0\nrecommendation_status: recommendation_ready\nrecommended_action: Organized Boarding"),
}


CONFIG_RULES = [
    ("seed", "يثبت العشوائية حتى يحصل الطلاب على نفس البيانات عند إعادة التشغيل. بدون seed، يصعب مقارنة نتائج طالبين أو شرح سبب اختلاف المخرجات."),
    ("trip_count", "عدد الرحلات التي ستولد. إذا كان العدد قليلا جدا، تصبح KPIs ضعيفة لأن العينة لا تكفي لدعم recommendation."),
    ("bus_capacity", "سعة الحافلة المستخدمة في فحص passenger_load. هذا الحقل يدخل في quality gate وليس في الشكل البصري فقط."),
    ("stops.problem_weight", "وزن المشكلة في كل محطة. محطة ذات وزن أعلى تظهر فيها احتمالات تأخير أكبر، فتتحول إلى hotspot في التحليل."),
    ("delay_causes", "تعريف أسباب التأخير وقيم base_seconds وvariability. هذا يجعل السبب النصي يتحول إلى أثر رقمي."),
    ("peak_hours", "الساعات التي يزيد فيها الضغط. تؤثر في load وtraffic_delay واحتمال بعض الأسباب."),
    ("on_time_threshold_sec", "الحد الذي يحدد هل trip ملتزمة بالوقت. تغيير هذا الحد يغير on_time_rate مباشرة."),
    ("dwell_excess_threshold_sec", "يحدد متى تصبح مدة التوقف أعلى من المتوقع. يساعد على فهم boarding problems."),
    ("high_load_ratio", "نسبة تحميل عالية مقارنة بسعة الحافلة. يمكن استخدامها لاحقا لتمييز ازدحام الركاب."),
    ("passing_score", "الحد الأدنى لجودة البيانات. إذا انخفض quality_score عن هذا الحد، يجب أن يحجب النظام التحليل أو يضعفه."),
    ("saving_factor", "نسبة التحسن المفترضة عند تطبيق scenario. قيمة أعلى تعني أن التدخل يقلل جزءا أكبر من issue_wait_sec."),
    ("cost_factor", "تبسيط تعليمي للكلفة أو صعوبة التنفيذ. يدخل في action_score حتى لا يكون القرار مبنيا على التحسن فقط."),
    ("feasibility", "مدى قابلية تنفيذ السيناريو. تدخل سهل التنفيذ قد يكون أفضل كبداية حتى لو لم يكن أعلى تحسن رقمي."),
]


KPI_DETAILS = [
    ("on_time_rate", "trips.final_delay_sec", "count(final_delay_sec <= threshold) / count(trips)", "يعطي صورة عامة عن موثوقية المسار. إذا كان منخفضا، فهذا لا يخبرنا أين المشكلة، لكنه يقول إن المسار يحتاج تفتيشا أعمق."),
    ("avg_final_delay_sec", "trips.final_delay_sec", "mean(final_delay_sec)", "يعرض متوسط التأخير عند نهاية الرحلة. هذا مفيد لقياس أثر السيناريوهات لأن أي تحسن في المحطات يجب أن يظهر في نهاية الرحلة."),
    ("avg_dwell_time_sec", "stop_events.dwell_time_sec", "mean(dwell_time_sec)", "يركز على وقت توقف الحافلة عند المحطات. إذا كان عاليا في محطة معينة فقد يشير إلى boarding أو ازدحام ركاب."),
    ("worst_stop", "stop_events grouped by stop_id", "highest avg_added_delay_sec", "يحدد نقطة البداية للتحقيق. لا يعني القرار النهائي، لكنه يوجه المستخدم إلى مكان التأخير الأكبر."),
    ("cause_summary", "stop_events.delay_cause", "sum(added_delay_sec) by cause", "يوضح هل المشكلة أقرب إلى boarding أو traffic أو schedule_gap. هذا يساعد على اختيار scenario مناسب."),
    ("trip_summary", "trips.final_delay_sec", "top delayed trips", "يعطي أمثلة محددة يمكن فتحها في Delay Evidence بدلا من الاكتفاء بمتوسط عام."),
]


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def inline(text: str) -> str:
    safe = escape(text)
    safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
    safe = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", safe)
    return safe


def markdown_to_html(source: str) -> str:
    blocks: list[str] = []
    lines = source.replace("دفتر Jupyter", "Jupyter Notebook").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")), 4)
            blocks.append(f"<h{level}>{inline(line.lstrip('#').strip())}</h{level}>")
            i += 1
            continue
        if line.strip().startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s", lines[i]):
                item = re.sub(r"^\s*\d+\.\s", "", lines[i].strip())
                items.append(f"<li>{inline(item)}</li>")
                i += 1
            blocks.append("<ol>" + "".join(items) + "</ol>")
            continue
        if line.strip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            blocks.append(markdown_table(rows))
            continue
        paragraph = [line]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not lines[i].startswith("#")
            and not lines[i].strip().startswith("- ")
            and not re.match(r"^\s*\d+\.\s", lines[i])
            and not lines[i].strip().startswith("|")
        ):
            paragraph.append(lines[i].strip())
            i += 1
        blocks.append("<p>" + inline(" ".join(paragraph)) + "</p>")
    return "\n".join(blocks)


def curated_markdown_to_html(number: int, fallback_source: str) -> str:
    content = CURATED_MARKDOWN.get(number)
    if not content:
        return markdown_to_html(fallback_source)
    paragraphs = "".join(f"<p>{inline(paragraph)}</p>" for paragraph in content.get("paragraphs", []))
    bullets = ""
    if content.get("bullets"):
        bullets = "<ul>" + "".join(f"<li>{inline(item)}</li>" for item in content["bullets"]) + "</ul>"
    return f"<h2>{inline(content['title'])}</h2>{paragraphs}{bullets}"


def markdown_table(rows: list[str]) -> str:
    html_rows = []
    for index, row in enumerate(rows):
        if set(row.replace("|", "").strip()) <= {"-", ":"}:
            continue
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        tag = "th" if index == 0 else "td"
        html_rows.append("<tr>" + "".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in cells) + "</tr>")
    return '<div class="table-wrap"><table>' + "".join(html_rows) + "</table></div>"


def explain_cell(number: int) -> str:
    paragraphs = CELL_EXPLANATIONS.get(
        number,
        ["هذه الخلية جزء من تسلسل notebook. اقرأها مع الخلية السابقة واللاحقة حتى يظهر مكانها في pipeline."]
    )
    return "".join(f"<p>{escape(paragraph)}</p>" for paragraph in paragraphs)


def code_learning_value(number: int) -> str:
    values = {
        7: [
            ("ماذا يتعلم الطالب هنا؟", "أن config هو عقد تعليمي وتشغيلي. إذا أردنا تجربة عالم مختلف، نغير القواعد لا نعيد كتابة الدالة."),
            ("مثال", "رفع trip_count يزيد حجم العينة. رفع problem_weight في S03 يجعل المحطة تظهر كمشكلة أكبر. تغيير saving_factor يجعل scenario أكثر أو أقل تفاؤلا."),
            ("خطأ شائع", "اعتبار config مجرد أرقام. في الحقيقة كل قيمة هنا ستتحول إلى صفوف ثم KPIs ثم recommendation."),
        ],
        9: [
            ("ماذا يتعلم الطالب هنا؟", "أن توليد البيانات ليس random rows. التوليد الجيد يحافظ على العلاقات: كل trip لها stop_events، وكل stop_event له trip_id وstop_id يمكن تتبعهما."),
            ("مثال", "إذا كانت T001 تمر على خمس محطات، يجب أن تظهر خمس rows في stop_events لهذه الرحلة. عند آخر محطة يظهر cumulative_delay_sec الذي يصبح final_delay_sec في trips."),
            ("خطأ شائع", "حساب التأخير مباشرة في trips ونسيان stop_events. هذا يمنع الطالب من معرفة أين حدث التأخير ولماذا."),
        ],
        15: [
            ("ماذا يتعلم الطالب هنا؟", "أن validation ليس اختبارا بعديا فقط. هو gate داخل المنتج يمنع نتائج غير موثوقة من الوصول إلى المستخدم."),
            ("مثال", "إذا كان stop_id في stop_events غير موجود في stops، فإن أي map أو explorer سيعرض دليلا بلا موقع صحيح."),
            ("خطأ شائع", "الاكتفاء برسالة Data OK. المطلوب معرفة أي check نجح أو فشل، severity، وعدد الصفوف المتأثرة."),
        ],
        17: [
            ("ماذا يتعلم الطالب هنا؟", "أن KPI يبدأ بسؤال ثم source table ثم formula. الرقم في الواجهة هو آخر خطوة وليس أول خطوة."),
            ("مثال", "on_time_rate يستخدم trips لأن السؤال عن الرحلة كاملة، بينما worst_stop يستخدم stop_events لأن السؤال عن محطة داخل الرحلات."),
            ("خطأ شائع", "استخدام stop_events لحساب عدد الرحلات مباشرة. هذا يضاعف العد لأن كل trip تظهر في عدة stops."),
        ],
        20: [
            ("ماذا يتعلم الطالب هنا؟", "أن scenario يجب أن يغير البيانات ثم يعيد الحساب. إذا غيرنا البطاقة في الواجهة فقط، فهذا ليس DSS بل mockup."),
            ("مثال", "Organized Boarding يقلل issue_wait في S03، ثم ينخفض added_delay، ثم يعاد cumulative_delay، ثم يتغير final_delay_sec."),
            ("خطأ شائع", "مقارنة scenario بدون baseline محفوظ. عندها لا نعرف هل التحسن حقيقي أم نتيجة تعديل خاطئ."),
        ],
        22: [
            ("ماذا يتعلم الطالب هنا؟", "أن recommendation هي data object وليست عبارة تسويقية. يجب أن تحتوي evidence وconfidence وlimitations."),
            ("مثال", "التوصية تقول Organized Boarding، لكنها تربطها بـ S03 وbaseline وscenario improvement وتذكر أن البيانات synthetic."),
            ("خطأ شائع", "إخفاء القيود حتى تبدو النتيجة أقوى. في الأنظمة المهنية، ذكر القيود يزيد الثقة لأنه يوضح حدود الاستخدام."),
        ],
        24: [
            ("ماذا يتعلم الطالب هنا؟", "أن pipeline هو ترتيب مسؤول للعمليات. كل مرحلة لها input وoutput، والمرحلة التالية تعتمد عليها."),
            ("مثال", "API /api/kpis لا يحتاج أن يعرف كيف تولدت البيانات خطوة بخطوة؛ يستدعي pipeline ويأخذ analysis."),
            ("خطأ شائع", "تشغيل analysis منفصلا على بيانات قديمة أو غير مفحوصة. pipeline يقلل هذا الخطر."),
        ],
    }
    if number not in values:
        return ""
    cards = "".join(f"<article><strong>{escape(title)}</strong><p>{escape(body)}</p></article>" for title, body in values[number])
    return f'<section class="learning-value">{cards}</section>'


def function_panels(source: str) -> str:
    panels = []
    for name, detail in FUNCTION_DETAILS.items():
        if f"def {name}" not in source:
            continue
        paragraphs = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in detail["paragraphs"])
        panels.append(
            f"""
            <section class="function-note">
              <header>
                <span>Function explanation</span>
                <h3>{escape(name)}()</h3>
                <code>{escape(detail["file"])}</code>
              </header>
              <div>{paragraphs}</div>
              <aside><strong>مثال تطبيقي</strong><p>{escape(detail["example"])}</p></aside>
            </section>
            """
        )
    return "".join(panels)


def output_panel(number: int) -> str:
    if number not in OUTPUTS:
        return ""
    title, body, code = OUTPUTS[number]
    return f"""
    <section class="output">
      <header><strong>{escape(title)}</strong><span>Expected output</span></header>
      <pre>{escape(code)}</pre>
      <p>{escape(body)}</p>
    </section>
    """


def bullet_list(items: list[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def week_panel(number: int) -> str:
    week = CELL_WEEK.get(number, 1)
    item = WEEK_GUIDANCE[week]
    return f"""
    <section class="week-panel week-{week}">
      <header>
        <span class="week-number">الأسبوع {week}</span>
        <div>
          <strong>{escape(item["phase"])}</strong>
          <small>{escape(item["label"])}</small>
        </div>
      </header>
      <p>{escape(item["summary"])}</p>
      <div class="week-grid">
        <article>
          <b>يعرف</b>
          <ul>{bullet_list(item["know"])}</ul>
        </article>
        <article>
          <b>ينفذ</b>
          <ul>{bullet_list(item["execute"])}</ul>
        </article>
        <article>
          <b>يختبر</b>
          <ul>{bullet_list(item["test"])}</ul>
        </article>
      </div>
      <div class="report-tasks">
        <strong>مهام تقرير الطالب</strong>
        <ul>{bullet_list(item["report"])}</ul>
      </div>
    </section>
    """


def week_overview() -> str:
    cards = "".join(
        f"""
        <article class="week-card week-{number}">
          <span>الأسبوع {number}</span>
          <h3>{escape(item["phase"])}</h3>
          <p>{escape(item["summary"])}</p>
          <strong>مخرج التقرير</strong>
          <ul>{bullet_list(item["report"][:2])}</ul>
        </article>
        """
        for number, item in WEEK_GUIDANCE.items()
    )
    return f"""
    <section class="week-overview">
      <div class="section-heading">
        <span>خارطة التنفيذ</span>
        <h2>كيف يقرأ الطالب هذا Jupyter Notebook خلال أربعة أسابيع؟</h2>
        <p>كل جزء في الصفحة يحمل بطاقة أسبوعية توضّح ما يجب فهمه، ما يجب تشغيله، ما يجب اختباره، وما الذي يمكن توثيقه في التقرير النهائي.</p>
      </div>
      <div class="week-cards">{cards}</div>
    </section>
    """


def code_cell(number: int, source: str) -> str:
    parts = split_code(source)
    rendered = []
    for index, part in enumerate(parts, 1):
        rendered.append(
            f"""
            <div class="code-part">
              <div class="part-title">Code block {index}</div>
              <pre class="code-block"><code>{escape(part)}</code></pre>
              {function_panels(part)}
            </div>
            """
        )
    return f"""
    <article class="cell code" id="cell-{number}">
      <div class="prompt">In [{number}]</div>
      <div class="cell-body">
        {week_panel(number)}
        {''.join(rendered)}
        <section class="explain">
          <strong>شرح الخلية</strong>
          {explain_cell(number)}
        </section>
        {code_learning_value(number)}
        {output_panel(number)}
      </div>
    </article>
    """


def split_code(source: str) -> list[str]:
    if len(source) < 1500:
        return [source]
    chunks: list[str] = []
    current: list[str] = []
    for line in source.splitlines():
        if line.startswith("def ") and current:
            chunks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current).strip())
    return [chunk for chunk in chunks if chunk]


def concept_sections() -> str:
    config_cards = "".join(
        f"<article><code>{escape(name)}</code><p>{escape(body)}</p></article>"
        for name, body in CONFIG_RULES
    )
    kpi_cards = "".join(
        f"""
        <article>
          <h3>{escape(name)}</h3>
          <dl>
            <dt>Source</dt><dd><code>{escape(source)}</code></dd>
            <dt>Formula</dt><dd><code>{escape(formula)}</code></dd>
          </dl>
          <p>{escape(body)}</p>
        </article>
        """
        for name, source, formula, body in KPI_DETAILS
    )
    return f"""
    <section class="deep-section" id="config-rules">
      <h2>شرح قواعد التوليد وملفات config</h2>
      <p>قبل قراءة الدوال، يحتاج الطالب أن يفهم أن كثيرا من سلوك النظام يأتي من config وليس من الواجهة. هذه القواعد هي التي تغير شكل البيانات ثم تغير نتائج التحليل.</p>
      <div class="concept-grid">{config_cards}</div>
    </section>
    <section class="deep-section" id="kpi-rules">
      <h2>شرح KPIs المستخدمة في المشروع</h2>
      <p>كل KPI هنا له source وformula ومعنى تشغيلي. الهدف ليس حفظ الاسم، بل فهم كيف يتحول الصف في الجدول إلى رقم يظهر في Dashboard أو Recommendation.</p>
      <div class="kpi-grid">{kpi_cards}</div>
    </section>
    """


def build() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = []
    toc = []
    for number, cell in enumerate(notebook["cells"], 1):
        source = "".join(cell.get("source", []))
        heading = next((line.lstrip("#").strip().replace("دفتر Jupyter", "Jupyter Notebook") for line in source.splitlines() if line.strip().startswith("#")), None)
        if heading:
            toc_title = CURATED_MARKDOWN.get(number, {}).get("title", heading)
            toc.append((number, toc_title))
        if cell["cell_type"] == "markdown":
            cells.append(
                f"""
                <article class="cell markdown" id="cell-{number}">
                  <div class="prompt">Markdown</div>
                  <div class="cell-body">
                    {week_panel(number)}
                    {curated_markdown_to_html(number, source)}
                  </div>
                </article>
                """
            )
        else:
            cells.append(code_cell(number, source))

    toc_links = "".join(f'<a href="#cell-{number}"><b>{index}</b><span>{escape(title)}</span></a>' for index, (number, title) in enumerate(toc, 1))

    html_doc = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Bus Delay DSS - Jupyter Notebook</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap" rel="stylesheet" />
<style>
:root{{--bg:#f4f7fb;--paper:#fff;--line:#d9e5ee;--text:#102033;--muted:#60758b;--blue:#087da8;--green:#08734d;--amber:#9a5514;--code-bg:#f8fafc;--code-line:#d8e4ec;}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:var(--bg);color:var(--text);font-family:Tajawal,Arial,sans-serif;line-height:1.8}} code,pre{{font-family:Consolas,"Courier New",monospace;direction:ltr;text-align:left}} a{{color:inherit}}
.page{{max-width:1180px;margin:0 auto;padding:28px 24px 70px}}
.hero{{background:linear-gradient(135deg,#fff,#eef8fc);border:1px solid var(--line);border-radius:18px;padding:28px;box-shadow:0 12px 30px rgba(20,32,51,.08);margin-bottom:18px}}
.hero-row{{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}} .badge{{display:inline-flex;border:1px solid #c7e7f6;background:#e7f4fb;color:var(--blue);border-radius:999px;padding:6px 12px;font-weight:900;direction:ltr}}
h1{{font-size:42px;margin:12px 0 10px;letter-spacing:0}} .hero p{{max-width:920px;color:#40536a;font-size:18px;margin:0 0 12px}} .open-app{{display:inline-flex;text-decoration:none;background:var(--blue);color:white;border-radius:999px;padding:11px 16px;font-weight:900;white-space:nowrap}}
.week-overview{{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 26px rgba(20,32,51,.07)}} .section-heading span{{display:inline-flex;background:#eef8fc;border:1px solid #c7e7f6;color:var(--blue);border-radius:999px;padding:5px 10px;font-weight:900}} .section-heading h2{{margin:10px 0 8px;font-size:25px}} .section-heading p{{margin:0 0 16px;color:#40536a}}
.week-cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}} .week-card{{--week:#087da8;--week-bg:#eef8fc;background:linear-gradient(180deg,var(--week-bg),#fff);border:1px solid color-mix(in srgb,var(--week) 32%,#d9e5ee);border-radius:14px;padding:15px;box-shadow:0 8px 18px rgba(20,32,51,.05)}} .week-card span{{display:inline-flex;background:var(--week);color:white;border-radius:999px;padding:4px 10px;font-weight:900}} .week-card h3{{margin:10px 0 6px;font-size:18px}} .week-card p{{margin:0 0 10px;color:#40536a}} .week-card strong{{color:var(--week)}} .week-card ul{{margin:6px 0 0;padding-inline-start:22px;color:#40536a}}
.week-1{{--week:#087da8;--week-bg:#eef8fc}} .week-2{{--week:#08734d;--week-bg:#effcf6}} .week-3{{--week:#9a5514;--week-bg:#fff7ed}} .week-4{{--week:#5b4cc4;--week-bg:#f4f2ff}}
.week-panel{{--week:#087da8;--week-bg:#eef8fc;border:1px solid color-mix(in srgb,var(--week) 32%,#d9e5ee);background:linear-gradient(180deg,var(--week-bg),#fff);border-radius:14px;padding:14px;margin-bottom:16px}} .week-panel header{{display:flex;align-items:center;gap:12px;margin-bottom:8px}} .week-number{{display:grid;place-items:center;min-width:78px;background:var(--week);color:white;border-radius:999px;padding:6px 12px;font-weight:900}} .week-panel header strong{{display:block;color:#102033;font-size:18px}} .week-panel header small{{display:block;color:#60758b;direction:ltr;text-align:right}} .week-panel p{{margin:0 0 10px;color:#40536a}} .week-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}} .week-grid article,.report-tasks{{background:rgba(255,255,255,.76);border:1px solid var(--line);border-radius:12px;padding:12px}} .week-grid b,.report-tasks strong{{display:block;color:var(--week);font-size:16px;margin-bottom:4px}} .week-grid ul,.report-tasks ul{{margin:0;padding-inline-start:22px;color:#30455b}} .week-grid li,.report-tasks li{{margin:4px 0}} .report-tasks{{margin-top:10px;background:#fff}}
.toc,.deep-section{{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:18px;margin-bottom:18px;box-shadow:0 8px 22px rgba(20,32,51,.06)}} .toc h2,.deep-section h2{{margin:0 0 10px;font-size:22px}} .toc-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:8px}}
.toc a{{display:grid;grid-template-columns:30px 1fr;gap:9px;text-decoration:none;border:1px solid var(--line);border-radius:12px;background:#fbfdff;padding:10px;align-items:center}} .toc b{{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#e7f4fb;color:var(--blue);direction:ltr}} .toc span{{line-height:1.4}}
.concept-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}} .concept-grid article,.kpi-grid article{{background:#fbfdff;border:1px solid var(--line);border-radius:12px;padding:14px}} .concept-grid code{{display:inline-flex;background:#eef8fc;color:#075c7e;border-radius:999px;padding:5px 9px;font-weight:900}} .concept-grid p,.kpi-grid p,.deep-section p{{color:#40536a;margin:8px 0 0}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:12px}} .kpi-grid h3{{direction:ltr;text-align:left;margin:0 0 8px;color:#075c7e}} .kpi-grid dl{{margin:0;display:grid;grid-template-columns:80px 1fr;gap:5px 8px}} .kpi-grid dt{{font-weight:900;color:#496479}} .kpi-grid dd{{margin:0}}
.notebook{{display:grid;gap:14px}} .cell{{display:grid;grid-template-columns:86px minmax(0,1fr);background:var(--paper);border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:0 8px 22px rgba(20,32,51,.05)}} .prompt{{background:#eef3f7;border-left:1px solid var(--line);padding:16px 10px;color:#52677c;font-weight:900;text-align:center;direction:ltr;font-size:13px}} .cell-body{{padding:20px;min-width:0}}
.markdown h1,.markdown h2,.markdown h3{{margin:0 0 12px}} .markdown p{{margin:0 0 12px;color:#30455b}} .markdown ul,.markdown ol{{margin:0 0 12px;padding-inline-start:26px}} .markdown li{{margin:5px 0;color:#30455b}} .markdown code{{background:#eef8fc;color:#075c7e;border-radius:6px;padding:2px 5px}}
.part-title{{display:inline-flex;background:#e7f4fb;color:#075c7e;border:1px solid #c7e7f6;border-radius:999px;padding:5px 10px;font-weight:900;margin:0 0 8px;direction:ltr}} .code-part + .code-part{{margin-top:14px}}
.code-block{{margin:0;background:var(--code-bg);color:#0f2338;border:1px solid var(--code-line);border-radius:12px;padding:16px;overflow:auto;font-size:13px;line-height:1.68;box-shadow:inset 4px 0 0 #c7e7f6}} .code-block code{{white-space:pre}}
.explain,.output,.function-note,.learning-value{{margin-top:14px;border-radius:12px;padding:16px;border:1px solid var(--line);background:#fbfdff}} .explain{{border-color:#c7e7f6;background:#f2fbff}} .explain strong{{color:#075c7e;font-size:18px}} .explain p,.output p,.function-note p{{margin:8px 0 0;color:#40536a}}
.learning-value{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;background:#fff;border-color:#dbe7ef}} .learning-value article{{background:#f8fbfd;border:1px solid var(--line);border-radius:10px;padding:12px}} .learning-value strong{{color:#075c7e}} .learning-value p{{margin:6px 0 0;color:#40536a}}
.output{{background:#fff8ef;border-color:#fed7aa}} .output header{{display:flex;justify-content:space-between;gap:10px;align-items:center}} .output header span{{color:var(--amber);font-weight:900;direction:ltr;font-size:12px}} .output pre{{background:white;border:1px solid #fed7aa;border-radius:10px;padding:12px;overflow:auto;white-space:pre-wrap;margin:10px 0;color:#3b2f20}}
.function-note{{background:#effcf6;border-color:#bdebd5}} .function-note header{{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:start;margin-bottom:8px}} .function-note header span{{color:var(--green);font-weight:900;direction:ltr;text-align:left;font-size:12px}} .function-note h3{{direction:ltr;text-align:left;margin:0;color:#075c3f;font-size:24px}} .function-note header code{{grid-column:2;grid-row:1 / span 2;background:white;border:1px solid #d7f3e6;border-radius:999px;padding:6px 10px;color:#244538}} .function-note aside{{margin-top:12px;background:white;border:1px solid #d7f3e6;border-radius:10px;padding:12px}} .function-note aside strong{{color:#075c3f}}
.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px;margin:10px 0}} table{{width:100%;border-collapse:collapse;background:#fff}} th,td{{padding:9px;border-bottom:1px solid var(--line);text-align:right}} th{{background:#edf5fa}} .footer{{margin-top:22px;color:var(--muted);text-align:center}}
@media(max-width:1050px){{.week-cards{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:900px){{.learning-value,.week-grid{{grid-template-columns:1fr}}}}
@media(max-width:760px){{.page{{padding:16px}}.hero-row,.output header{{flex-direction:column;align-items:flex-start}}h1{{font-size:31px}}.cell{{grid-template-columns:1fr}}.prompt{{border-left:0;border-bottom:1px solid var(--line);text-align:left}}.function-note header{{grid-template-columns:1fr}}.function-note header code{{grid-column:auto;grid-row:auto}}}}
@media(max-width:620px){{.week-cards{{grid-template-columns:1fr}}.week-panel header{{align-items:flex-start;flex-direction:column}}}}
</style>
</head>
<body>
<main class="page">
  <section class="hero">
    <div class="hero-row">
      <div>
        <span class="badge">Jupyter Notebook</span>
        <h1>Bus Delay DSS - Jupyter Notebook</h1>
        <p>{escape(INTRO.strip()).replace(chr(10) + chr(10), "</p><p>")}</p>
      </div>
      <a class="open-app" href="/">العودة إلى DSS</a>
    </div>
  </section>
  {week_overview()}
  <section class="toc"><h2>محتويات Jupyter Notebook</h2><div class="toc-grid">{toc_links}</div></section>
  {concept_sections()}
  <section class="notebook">{''.join(cells)}</section>
  <p class="footer">Generated from notebooks/bus_delay_full_journey_expanded.ipynb</p>
</main>
</body>
</html>"""
    OUTPUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
