export const buildPlan = [
  {
    week: "Week 1",
    ar: "الأسبوع الأول",
    title: "تثبيت الفكرة وبناء أساس المنتج",
    objective:
      "في هذا الأسبوع لا يبدأ الطالب من الرسم أو الكود مباشرة. يبدأ من فهم المشكلة وتحويلها إلى قرار واضح، ثم يثبت أن repo يعمل وأن الملفات الأساسية مفهومة. الهدف أن يعرف الطالب لماذا يوجد النظام، ومن سيستخدمه، وما الذي يجب أن ينتجه قبل الدخول في التحليل.",
    tasks: [
      {
        name: "تأطير المشكلة والقرار",
        purpose:
          "يصيغ الطالب المشكلة بطريقة قابلة للبناء البرمجي: ليست مشكلة عامة عن النقل، بل حالة قرار محددة تحتاج بيانات ومؤشرات وتوصية.",
        files: ["config/problem_scope.json", "README.md", "workbook/slice-01-overview.md"],
        page: "تعريف القرار",
        target: "overview",
        api: "GET /api/project",
        action:
          "يفتح صفحة تعريف القرار، يقرأ المشكلة وصاحب القرار والنطاق، ثم يراجع ملف problem_scope.json ليرى كيف تتحول الجمل إلى حقول منظمة يقرأها Backend.",
        evidence:
          "لقطة من صفحة تعريف القرار، ولقطة أو مقتطف من problem_scope.json، وفقرة قصيرة تشرح ما القرار الذي يدعمه DSS ولماذا لا يكفي Dashboard فقط.",
      },
      {
        name: "تشغيل repo وفهم مكوناته",
        purpose:
          "يتأكد الطالب أن البيئة تعمل، وأن هناك Backend وFrontend واختبارات وليست واجهة معزولة.",
        files: ["requirements.txt", "backend/main.py", "frontend/src/App.jsx", "tests/test_pipeline.py"],
        page: "ملفات repo",
        target: "structure",
        api: "GET /api/repo/tree",
        action:
          "يشغل أوامر التثبيت والاختبار، ثم يفتح صفحة ملفات repo ويحدد أين توجد إعدادات المشروع، منطق Python، الواجهة، والاختبارات.",
        evidence:
          "نتيجة pytest، لقطة من صفحة ملفات repo، وجدول صغير يربط كل مجلد بدوره: config للقرارات، backend للحساب، frontend للعرض، tests للتحقق.",
      },
    ],
  },
  {
    week: "Week 2",
    ar: "الأسبوع الثاني",
    title: "بناء البيانات وفحص جودتها",
    objective:
      "الطالب يتعلم أن أي DSS لا يبدأ من chart، بل من نموذج بيانات يمكن الدفاع عنه. في هذا الأسبوع يفهم الجداول، مفاتيح الربط، قواعد توليد البيانات، وحدود الجودة التي تمنع التحليل الضعيف.",
    tasks: [
      {
        name: "فهم ERD ومفاتيح الجداول",
        purpose:
          "يربط الطالب بين routes وstops وtrips وstop_events ويفهم أن stop_events هو جدول الأحداث الذي يغذي معظم التحليل.",
        files: ["backend/generator.py", "backend/main.py", "data/sample/*.csv"],
        page: "نموذج البيانات",
        target: "model",
        api: "GET /api/data-model",
        action:
          "يفتح نموذج البيانات، يضغط على كل جدول، يقرأ PK وFK، ثم يفتح عينة live من كل جدول ليتأكد أن العلاقات ليست رسما فقط.",
        evidence:
          "لقطة من ERD، عينة من جدول stop_events، وشرح لماذا route_id يربط route بالرحلات والمحطات، ولماذا trip_id + stop_id يصف حدث وصول الحافلة إلى محطة.",
      },
      {
        name: "توليد Synthetic Data وتفسير الافتراضات",
        purpose:
          "يتعلم الطالب أن البيانات التدريبية يجب أن تكون قابلة للتكرار ومبنية على قواعد واضحة، لا أرقام عشوائية بلا تفسير.",
        files: ["config/generation_rules.json", "backend/generator.py", "scripts/generate_sample_data.py"],
        page: "مختبر البيانات",
        target: "lab",
        api: "POST /api/generate",
        action:
          "يراجع seed وعدد الرحلات وساعات الذروة والمحطة ذات الوزن الأعلى، ثم يشغل التوليد ويفحص CSV الناتج.",
        evidence:
          "لقطة من مختبر البيانات، مقتطف من generation_rules.json، وCSV أو JSON output يوضح عدد الرحلات والمحطات وأحداث التوقف.",
      },
      {
        name: "بوابة الجودة قبل التحليل",
        purpose:
          "يتعلم الطالب أن النظام الجيد لا يثق بالبيانات تلقائيا. يجب أن توجد checks تمنع التوصية عندما تكون البيانات ناقصة أو غير منطقية.",
        files: ["config/validation_rules.json", "backend/validation.py", "data/sample/validation_report.json"],
        page: "بوابة الجودة",
        target: "quality",
        api: "GET /api/data-quality",
        action:
          "يفتح تقرير الجودة، يقرأ كل check، ثم يشرح ماذا قد يحدث لو فشل هذا الفحص ومع ذلك عرض النظام توصية.",
        evidence:
          "validation_report.json، لقطة من Quality Gate، وشرح قصير لمعنى quality score وعلاقته بثقة القرار.",
      },
    ],
  },
  {
    week: "Week 3",
    ar: "الأسبوع الثالث",
    title: "تحويل البيانات إلى DSS تشغيلي",
    objective:
      "هنا ينتقل الطالب من البيانات إلى الاستخدام. المطلوب ليس إنشاء مؤشرات كثيرة، بل بناء صفحات تساعد المستخدم على تحديد الحالة، فهم السبب، مقارنة التدخلات، ومعرفة لماذا يوصي النظام بخطوة معينة.",
    tasks: [
      {
        name: "قراءة Dashboard كمساحة قرار",
        purpose:
          "يتعلم الطالب أن Dashboard داخل DSS يجب أن يبرز الحالات الجاهزة للتحقيق، لا أن يعرض كل شيء بالتساوي.",
        files: ["backend/analysis.py", "config/kpi_config.json", "frontend/src/App.jsx"],
        page: "مساحة DSS",
        target: "dashboard",
        api: "GET /api/kpis",
        action:
          "يفتح مساحة DSS، يقرأ Priority Queue ومؤشرات Route B12، ثم يختار حالة واحدة ويشرح لماذا ظهرت كأولوية.",
        evidence:
          "لقطة من Dashboard، API response من /api/kpis، وفقرة تربط worst stop وaverage delay وpassenger impact بالحالة المختارة.",
      },
      {
        name: "استكشاف الدليل وراء الرقم",
        purpose:
          "يتعلم الطالب ألا يكتفي بقيمة KPI. يجب أن يعرف الصفوف والحقول التي صنعت هذا الرقم.",
        files: ["backend/analysis.py", "data/sample/stop_events.csv", "workbook/slice-05-dashboard.md"],
        page: "استكشاف الدليل",
        target: "explorer",
        api: "GET /api/kpis",
        action:
          "يفتح Evidence Explorer، يقارن المحطات، ويشرح أي stop أو segment يحتاج متابعة بناء على البيانات وليس الانطباع.",
        evidence:
          "لقطة من Evidence Explorer، عينة rows من stop_events، وشرح للحقول added_delay_sec وpassenger_load وdelay_cause.",
      },
      {
        name: "مقارنة السيناريوهات قبل التوصية",
        purpose:
          "يتعلم الطالب أن التدخل يجب أن يقارن ببدائل. الأفضل ليس دائما الأعلى تحسنا؛ قد يكون الأقل تكلفة أو الأعلى ثقة أو الأسهل للتجربة.",
        files: ["config/scenarios.json", "backend/scenarios.py", "data/sample/scenario_results.json"],
        page: "مختبر السيناريوهات",
        target: "scenario",
        api: "GET /api/scenarios",
        action:
          "يفتح Scenario Lab، يقرأ التحسن المتوقع والثقة وAction Score، ثم يشرح لماذا فاز سيناريو معين أو لماذا يحتاج Review.",
        evidence:
          "scenario_results.json، لقطة من Scenario Lab، ومقارنة قصيرة بين سيناريوهين على الأقل.",
      },
    ],
  },
  {
    week: "Week 4",
    ar: "الأسبوع الرابع",
    title: "التوصية، العرض، والتوثيق",
    objective:
      "الأسبوع الأخير يحول العمل إلى قصة قابلة للمراجعة. الطالب لا يقدم كود فقط، بل يشرح رحلة القرار كاملة: المشكلة، البيانات، الجودة، التحليل، السيناريو، التوصية، القيود، والخطوة التالية.",
    tasks: [
      {
        name: "إنتاج توصية قابلة للمراجعة",
        purpose:
          "يتعلم الطالب الفرق بين رأي عام وتوصية DSS. التوصية يجب أن تحمل evidence وconfidence وlimitations وnext step.",
        files: ["backend/recommendation.py", "config/decision_card.json", "data/sample/recommendation.json"],
        page: "مخرج القرار",
        target: "recommendation",
        api: "GET /api/recommendation",
        action:
          "يفتح مخرج القرار، يقرأ التوصية، ثم يراجع JSON ليرى كيف تم تمثيل الثقة والدليل والقيود.",
        evidence:
          "recommendation.json، لقطة من مخرج القرار، وفقرة تشرح هل التوصية جاهزة للتجربة أم تحتاج بيانات إضافية.",
      },
      {
        name: "تجميع Evidence Pack",
        purpose:
          "يتعلم الطالب كيف يحول العمل الفني إلى ملف مراجعة مفهوم للمشرف أو لجنة التدريب.",
        files: ["presentation/final-report.md", "presentation/demo-script.md", "presentation/screenshots/"],
        page: "مهام البناء",
        target: "tasks",
        api: "Multiple API outputs",
        action:
          "يجمع لقطات الشاشة ونتائج API وCSV/JSON والاختبارات، ثم يضعها في تقرير أو عرض يشرح الرحلة وليس النتيجة فقط.",
        evidence:
          "ملف تقرير، demo script، screenshots، نتيجة pytest، ومقتطفات من API responses المستخدمة في العرض.",
      },
    ],
  },
];

const journey = [
  ["Problem", "ما المشكلة التشغيلية؟"],
  ["Config", "ما الافتراضات والقواعد؟"],
  ["Python", "كيف نحسب ونولد ونفحص؟"],
  ["API", "كيف تصل النتائج إلى الواجهة؟"],
  ["UI", "كيف يفهم المستخدم الحالة؟"],
  ["Evidence", "ما الدليل القابل للمراجعة؟"],
];

const decisionCases = [
  {
    id: "H-017",
    title: "تأخر صباحي متكرر",
    route: "B12",
    segment: "S03 → S04",
    priority: 86,
    delay: "6.2 دقيقة",
    passengers: "280 / يوم",
    cause: "ازدحام عند الصعود",
    confidence: "Medium",
    tone: "critical",
  },
  {
    id: "H-012",
    title: "تكدس بعد الظهر",
    route: "B12",
    segment: "S04 → S05",
    priority: 62,
    delay: "3.4 دقيقة",
    passengers: "140 / يوم",
    cause: "حمل ركاب مرتفع",
    confidence: "Low",
    tone: "warning",
  },
  {
    id: "H-024",
    title: "تذبذب زمن الوصول",
    route: "B12",
    segment: "S02 → S03",
    priority: 54,
    delay: "2.8 دقيقة",
    passengers: "96 / يوم",
    cause: "فجوة في الجدولة",
    confidence: "Medium",
    tone: "normal",
  },
];

const slices = [
  {
    name: "Project Overview",
    ar: "تعريف القرار",
    file: "config/problem_scope.json",
    api: "GET /api/project",
    purpose: "يثبت المشكلة وصاحب القرار والنطاق قبل بناء أي Dashboard.",
    evidence: "لقطة صفحة القرار + فقرة توضّح لماذا هذا DSS وليس Dashboard فقط.",
  },
  {
    name: "Data Model",
    ar: "نموذج البيانات",
    file: "backend/generator.py",
    api: "GET /api/data-model",
    purpose: "يوضح كيف تتحول الرحلات والمحطات والأحداث إلى جداول قابلة للتحليل.",
    evidence: "صورة النموذج + ملفات CSV في data/sample.",
  },
  {
    name: "Synthetic Data Lab",
    ar: "مختبر البيانات",
    file: "config/generation_rules.json",
    api: "POST /api/generate",
    purpose: "ينتج Training Data قابلة للتكرار من قواعد تشغيلية واضحة.",
    evidence: "نتيجة السكربت + ملفات CSV + لقطة شاشة.",
  },
  {
    name: "Data Quality",
    ar: "بوابة الجودة",
    file: "backend/validation.py",
    api: "GET /api/data-quality",
    purpose: "يمنع الانتقال إلى التحليل والتوصية إذا كانت البيانات غير موثوقة.",
    evidence: "validation_report.json + نتيجة pytest.",
  },
  {
    name: "Dashboard",
    ar: "لوحة الأداء",
    file: "backend/analysis.py",
    api: "GET /api/kpis",
    purpose: "يعرض أهم الحالات التشغيلية فقط: أين المشكلة؟ ما شدتها؟ وما الدليل؟",
    evidence: "لقطة Dashboard + شرح أسوأ محطة وحالة قرار واحدة.",
  },
  {
    name: "Scenario Lab",
    ar: "مختبر السيناريو",
    file: "backend/scenarios.py",
    api: "GET /api/scenarios",
    purpose: "يقارن التدخلات قبل طلب تنفيذ ميداني أو تجربة تشغيلية.",
    evidence: "scenario_results.json + تفسير Action Score.",
  },
  {
    name: "Recommendation",
    ar: "التوصية",
    file: "backend/recommendation.py",
    api: "GET /api/recommendation",
    purpose: "يحوّل التحليل إلى توصية قابلة للمراجعة مع الثقة والقيود والخطوة التالية.",
    evidence: "recommendation.json + لقطة التوصية + demo script.",
  },
];

