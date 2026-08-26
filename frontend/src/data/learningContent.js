export const walkthroughStations = [
  {
    id: "entry",
    title: "App Entry",
    ar: "تشغيل النظام",
    purpose:
      "هذه المحطة تثبت أن المشروع ليس ملف HTML منفصل. يوجد Backend يعمل كخدمة API، وFrontend يقرأ منه، واختبارات تتحقق من منطق البيانات. الطالب يجب أن يفهم نقطة البداية قبل قراءة أي صفحة.",
    open: ["backend/main.py", "frontend/src/App.jsx", "README.md"],
    commands: ["uvicorn backend.main:app --reload", "cd frontend && npm run dev", "python -m pytest"],
    page: "ابدأ هنا",
    target: "canvas",
    api: "GET /api/health",
    trace:
      "ابدأ من README، ثم افتح backend/main.py لترى endpoints، ثم افتح frontend/src/App.jsx لترى كيف يتم استدعاء API وعرض النتائج. بعد ذلك شغل pytest لتفهم أن الاختبار جزء من المنتج وليس خطوة اختيارية.",
    mistake:
      "الخطأ الشائع أن يشرح الطالب الواجهة فقط وينسى أن هناك خدمة Backend وAPI contract واختبارات. هذا يجعل المشروع يبدو كتصميم شاشة وليس system.",
    verbal:
      "يجب أن يستطيع الطالب أن يقول: هذا repo يحتوي Backend FastAPI، Frontend React، config files، generated data، وtests، والواجهة تعرض مخرجات API وليست أرقاما مخترعة.",
  },
  {
    id: "config",
    title: "Config Controls Behavior",
    ar: "الـConfig يتحكم في السلوك",
    purpose:
      "هذه المحطة تشرح فكرة مهمة في software design: ليس كل تغيير يحتاج تعديل كود. بعض الافتراضات يجب أن تكون في JSON حتى تكون قابلة للمراجعة والتعديل بأمان.",
    open: ["config/problem_scope.json", "config/generation_rules.json", "config/kpi_config.json", "config/scenarios.json"],
    commands: ["python scripts/generate_sample_data.py"],
    page: "ملفات repo",
    target: "structure",
    api: "GET /api/project",
    trace:
      "افتح ملفات config وقارن بينها: problem_scope يحدد المشكلة، generation_rules يحدد طريقة توليد البيانات، kpi_config يحدد thresholds، وscenarios يحدد التدخلات الممكنة.",
    mistake:
      "الخطأ الشائع أن يعدل الطالب formula داخل Python بينما المطلوب تعديل threshold أو assumption داخل config. هذا يخلط بين rules وlogic.",
    verbal:
      "يجب أن يستطيع الطالب أن يشرح الفرق بين config الذي يغير الافتراضات، وbackend code الذي يطبق المنطق، وUI التي تعرض النتيجة.",
  },
  {
    id: "generator",
    title: "Synthetic Data Generator",
    ar: "مولد البيانات",
    purpose:
      "هذه المحطة تشرح كيف تتحول قواعد التدريب إلى جداول. الهدف ليس جعل البيانات حقيقية، بل جعلها مفهومة وقابلة للتكرار حتى يتعلم الطالب بناء pipeline.",
    open: ["backend/generator.py", "config/generation_rules.json", "data/sample/routes.csv", "data/sample/stop_events.csv"],
    commands: ["python scripts/generate_sample_data.py"],
    page: "مختبر البيانات",
    target: "lab",
    api: "POST /api/generate",
    trace:
      "تتبع route_id وstops_config وtrip_count داخل generator.py. لاحظ كيف ينشأ routes ثم stops ثم trips ثم stop_events، وكيف يتراكم cumulative_delay_sec مع كل محطة.",
    mistake:
      "الخطأ الشائع أن يتعامل الطالب مع stop_events كجدول عادي فقط. هو جدول الحدث الرئيسي: رحلة محددة تصل إلى محطة محددة وفيها زمن وصول وحمل ركاب وسبب تأخير.",
    verbal:
      "يجب أن يستطيع الطالب أن يشرح لماذا stop_events أكثر تفصيلا من trips، ولماذا هو المصدر الأساسي للتحليل والسيناريوهات.",
  },
  {
    id: "model",
    title: "Data Model Review",
    ar: "مراجعة نموذج البيانات",
    purpose:
      "هذه المحطة تختبر فهم الطالب للعلاقات. بدون فهم ماذا يمثّل الصف الواحد؟ وPK وFK، سيشرح الطالب المؤشرات بشكل ضعيف لأنه لا يعرف ما الذي تم تجميعه.",
    open: ["backend/main.py", "backend/generator.py"],
    commands: ["Open /api/data-model"],
    page: "نموذج البيانات",
    target: "model",
    api: "GET /api/data-model",
    trace:
      "افتح ERD، ثم اضغط على routes وstops وtrips وstop_events. اربط route_id وtrip_id وstop_id بالحقول داخل الجداول، ثم افتح preview لكل جدول.",
    mistake:
      "الخطأ الشائع أن يخلط الطالب بين primary key وforeign key أو يظن أن كل key يعني نفس الشيء. PK يعرف الصف، وFK يربط الصف بجدول آخر.",
    verbal:
      "يجب أن يستطيع الطالب أن يقول: routes يحتوي تعريف المسار، stops يحتوي محطات المسار، trips يحتوي رحلات كاملة، وstop_events يحتوي حدث وصول الرحلة إلى محطة.",
  },
  {
    id: "kpi",
    title: "KPI Implementation",
    ar: "تنفيذ KPI",
    purpose:
      "هذه المحطة تجعل الطالب يتتبع KPI واحدا من السؤال إلى formula إلى API إلى UI. الهدف أن يفهم أن المؤشر قرار مصغر وليس رقما للعرض.",
    open: ["config/kpi_config.json", "backend/analysis.py", "frontend/src/App.jsx"],
    commands: ["Open /api/kpis"],
    page: "بناء المؤشرات",
    target: "kpi",
    api: "GET /api/kpis",
    trace:
      "اختر On-Time Rate مثلا. اقرأ threshold في kpi_config، ثم formula في analysis.py، ثم response في /api/kpis، ثم بطاقة العرض في DSS Workspace.",
    mistake:
      "الخطأ الشائع أن يقول الطالب: المؤشر يقيس الأداء. الإجابة الأقوى تذكر المصدر والformula والthreshold وحدود التفسير.",
    verbal:
      "يجب أن يستطيع الطالب أن يشرح KPI واحدا بعمق: السؤال، الجدول، الحقول، طريقة الحساب، مكان العرض، وخطر سوء التفسير.",
  },
  {
    id: "scenario",
    title: "Scenario Simulation",
    ar: "محاكاة السيناريو",
    purpose:
      "هذه المحطة تشرح الفرق بين عرض حالة حالية واختبار تدخل. Scenario Lab يحاول تقدير أثر تدخل قبل تحويله إلى recommendation.",
    open: ["config/scenarios.json", "backend/scenarios.py", "data/sample/scenario_results.json"],
    commands: ["Open /api/scenarios"],
    page: "مختبر السيناريوهات",
    target: "scenario",
    api: "GET /api/scenarios",
    trace:
      "افتح scenarios.json لترى saving_factor وcost_factor وfeasibility. ثم افتح scenarios.py لترى كيف يتم تعديل stop_events وإعادة حساب final_delay_sec وAction Score.",
    mistake:
      "الخطأ الشائع اختيار السيناريو الأعلى تحسنا فقط. القرار الأفضل يوازن improvement مع confidence وfeasibility وcost factor.",
    verbal:
      "يجب أن يستطيع الطالب أن يقول: السيناريو يغير افتراضا محددا في البيانات، ثم يعيد الحساب، ثم ينتج ranking signal وليس قرارا نهائيا.",
  },
  {
    id: "recommendation",
    title: "Recommendation Logic",
    ar: "منطق التوصية",
    purpose:
      "هذه المحطة تشرح كيف تتحول النتائج إلى مخرج قرار قابل للمراجعة. التوصية القوية لا تقول ماذا نفعل فقط، بل لماذا، وبأي ثقة، وما القيود.",
    open: ["backend/recommendation.py", "config/decision_card.json", "data/sample/recommendation.json"],
    commands: ["Open /api/recommendation"],
    page: "مخرج القرار",
    target: "recommendation",
    api: "GET /api/recommendation",
    trace:
      "افتح recommendation.py وتتبع كيف يختار النظام recommended_action وكيف يضيف evidence وconfidence وlimitations وnext step.",
    mistake:
      "الخطأ الشائع أن يكتب الطالب conclusion بدون limitations. في DSS، ذكر القيود ليس ضعفاً؛ هو جزء من جودة القرار.",
    verbal:
      "يجب أن يستطيع الطالب أن يشرح لماذا التوصية جاهزة للتجربة أو لماذا تحتاج بيانات إضافية قبل الاعتماد.",
  },
  {
    id: "frontend",
    title: "Frontend Rendering",
    ar: "عرض Frontend",
    purpose:
      "هذه المحطة تركز على React: كيف تتحول response objects إلى cards وcharts وtables. الهدف أن يعرف الطالب أين ينتهي backend وأين يبدأ UI.",
    open: ["frontend/src/App.jsx", "frontend/src/styles.css", "frontend/src/data/mockData.js"],
    commands: ["cd frontend && npm run dev"],
    page: "مساحة DSS",
    target: "dashboard",
    api: "GET /api/kpis + GET /api/scenarios + GET /api/recommendation",
    trace:
      "تتبع refreshData في App.jsx، ثم شاهد كيف تنتقل kpis وscenarios وrecommendation إلى components مثل Dashboard وScenarioLab وRecommendation.",
    mistake:
      "الخطأ الشائع أن يعدل الطالب النص أو اللون فقط ويظن أنه طور النظام. التطوير الحقيقي يربط state وAPI response وrendering وسلوك المستخدم.",
    verbal:
      "يجب أن يستطيع الطالب أن يشرح أن Frontend لا يحسب القرار الأساسي؛ هو يطلب البيانات ويعرضها بشكل يساعد المستخدم على الفهم.",
  },
  {
    id: "tests",
    title: "Tests and Debugging",
    ar: "الاختبارات والتصحيح",
    purpose:
      "هذه المحطة تجعل الاختبارات جزءا من القصة. الاختبار لا يثبت أن المنتج كامل، لكنه يحمي مسارات مهمة من الكسر.",
    open: ["tests/test_pipeline.py", "backend/pipeline.py"],
    commands: ["python -m pytest -q"],
    page: "ملفات repo",
    target: "structure",
    api: "No API: local verification",
    trace:
      "افتح test_pipeline.py وشاهد ما الذي يتم فحصه: الجداول، الجودة، KPIs، التوصية، data model، وrepo browser. ثم شغل pytest واقرأ النتيجة.",
    mistake:
      "الخطأ الشائع أن يقول الطالب: الاختبارات نجحت فقط. الإجابة الأقوى تشرح ماذا تغطي الاختبارات وماذا لا تغطي.",
    verbal:
      "يجب أن يستطيع الطالب أن يقول: pytest يحمي pipeline الأساسي، لكنه لا يغطي كل UI behavior أو جودة القرار في العالم الحقيقي.",
  },
];

export const verbalChecks = [
  {
    title: "تشغيل Backend وFrontend",
    summary: "شرح لماذا يحتاج المشروع إلى خدمتين تعملان معا.",
    explanation:
      "الطالب يجب أن يفرق بين Backend الذي يحسب ويقرأ الملفات وينتج API responses، وFrontend الذي يعرض هذه الاستجابات بطريقة مفهومة. تشغيل الواجهة وحدها يعطي شاشة، لكنه لا يثبت أن النظام يحسب فعلا. وتشغيل Backend وحده يعطي API، لكنه لا يشرح التجربة التي يراها المستخدم.",
    example:
      "مثال: عند فتح DSS Workspace، React يطلب GET /api/kpis. FastAPI يشغل pipeline، يحسب المؤشرات في analysis.py، ثم ترجع النتيجة إلى الواجهة وتظهر كبطاقات وخرائط وجداول.",
  },
  {
    title: "Config مقابل Backend logic مقابل Frontend rendering",
    summary: "شرح أين نغير الافتراض، أين نحسب، وأين نعرض.",
    explanation:
      "Config يستخدم لتعديل قواعد قابلة للمراجعة مثل route_id أو thresholds أو السيناريوهات. Backend logic يطبق الحسابات والتحقق والتوصية. Frontend rendering لا يجب أن يخترع القرار؛ دوره أن يوضح البيانات، يبرز الحالات، ويجعل المستخدم يرى العلاقة بين الدليل والقرار.",
    example:
      "مثال: إذا تغير حد التأخير المقبول من 300 إلى 240 ثانية، يبدأ التعديل من config/kpi_config.json. بعد ذلك analysis.py يستخدم الرقم الجديد، وDSS Workspace يعرض KPI الجديد بدون إعادة كتابة البطاقة نفسها.",
  },
  {
    title: "Data model وماذا يمثّل الصف الواحد؟ لكل جدول",
    summary: "شرح معنى الصف الواحد قبل شرح أي مؤشر.",
    explanation:
      "قبل حساب KPI يجب أن يعرف الطالب ماذا يمثل الصف. routes يصف المسار، stops يصف المحطات، trips يصف رحلة كاملة، وstop_events يصف وصول رحلة إلى محطة محددة. هذا يمنع خلط متوسط رحلة كاملة مع حدث محطة واحد.",
    example:
      "مثال: final_delay_sec موجود في trips لأنه يلخص نهاية الرحلة، أما added_delay_sec وpassenger_load فهما في stop_events لأنهما يحدثان عند محطة محددة داخل رحلة محددة.",
  },
  {
    title: "تتبع KPI من السؤال إلى الشاشة",
    summary: "شرح المؤشر كمسار كامل وليس رقم منفصل.",
    explanation:
      "KPI الجيد يبدأ بسؤال تشغيلي، ثم جدول مصدر، ثم حقول، ثم formula، ثم threshold، ثم مكان عرض، ثم تفسير وحدود. الطالب يجب أن يربط الرقم بالقرار الذي يخدمه، لا أن يقرأه كقيمة جميلة في Dashboard.",
    example:
      "مثال: On-Time Rate يبدأ من سؤال: هل الرحلات ملتزمة بحد التأخير؟ المصدر trips.final_delay_sec، والحد في config/kpi_config.json، والحساب في analysis.py، والعرض في Dashboard، والاستخدام هو تقدير موثوقية الخدمة.",
  },
  {
    title: "Scenario Lab كاختبار فرضية",
    summary: "شرح كيف تتغير البيانات عند اختبار تدخل.",
    explanation:
      "Scenario ليس prediction كامل ولا قرار نهائي. هو تجربة what-if مبسطة: نعدل افتراضا محددا مثل تقليل زمن الصعود في محطة معينة، ثم نعيد حساب التأخير ونقارن baseline مع scenario. لذلك يجب شرح improvement وconfidence وcost_factor معا.",
    example:
      "مثال: إذا كان السيناريو يقلل issue_wait_sec عند S04، فالأثر يجب أن يظهر في stop_events ثم trips ثم avg_final_delay_sec ثم Action Score.",
  },
  {
    title: "Recommendation مشروطة بالدليل",
    summary: "شرح لماذا لا تكفي النتيجة وحدها.",
    explanation:
      "التوصية في DSS يجب أن تحمل status وevidence وconfidence وlimitations وnext_step. إذا فشلت جودة البيانات أو كان الدليل غير كاف، النظام يجب أن يوقف التوصية أو يطلب review بدلا من إعطاء قرار واثق.",
    example:
      "مثال: Recommendation ready تعني أن جودة البيانات والسيناريو الأفضل يسمحان بتجربة pilot. لا تعني تنفيذ مباشر في المدينة بدون مراجعة تشغيلية وبيانات حقيقية.",
  },
  {
    title: "ما الذي تغطيه tests وما الذي لا تغطيه",
    summary: "شرح الاختبار كحماية تقنية وليس كضمان كامل.",
    explanation:
      "pytest يثبت أن pipeline الأساسي ما زال يعمل: الجداول تتولد، validation ينجح، KPIs موجودة، والتوصية قابلة للتفسير. لكنه لا يثبت أن UI مثالية، ولا أن البيانات الحقيقية ستتصرف مثل synthetic data.",
    example:
      "مثال: test_recommendation_is_explainable يتحقق من وجود status وrecommended_action وquality_score. لكنه لا يقرر هل التدخل هو الأفضل فعليا في الميدان.",
  },
];

export const featureFlowSteps = [
  {
    title: "1. ابدأ من سلوك المستخدم",
    code: "User need -> UI action",
    body:
      "لا تبدأ بإضافة endpoint مباشرة. اكتب أولا ماذا سيضغط المستخدم، ماذا يريد أن يرى، وما القرار أو الفهم الذي ستخدمه الميزة. هذا يحمي المشروع من إضافة API لا يستخدمه أحد.",
    example:
      "مثال: الطالب يريد زر يعرض رحلات الذروة فقط. إذن السلوك هو filter في الواجهة، وليس بالضرورة صفحة جديدة.",
  },
  {
    title: "2. حدد contract بين Frontend وBackend",
    code: "Request + Response shape",
    body:
      "قبل كتابة الكود، حدد اسم endpoint، method، query params أو body، وشكل response. Frontend وBackend يتفقان على هذا العقد. أي تغيير في أسماء الحقول قد يكسر الواجهة حتى لو الحساب صحيح.",
    example:
      "مثال: GET /api/trips?period=peak يرجع { rows, row_count, filters_applied }. الواجهة تعرف أنها ستقرأ rows ولا تبحث عن اسم عشوائي.",
  },
  {
    title: "3. ضع الحساب في المكان الصحيح",
    code: "backend/*.py",
    body:
      "إذا كانت الميزة تحتاج حساب KPI أو سيناريو أو validation، يجب أن يكون الحساب في Backend. React يعرض ويختار ويرسل الطلب، لكنه لا يصبح مصدر الحقيقة للحسابات.",
    example:
      "مثال: لا تحسب Priority Score داخل JSX. ضع formula في analysis.py أو recommendation.py ثم اعرض النتيجة من API.",
  },
  {
    title: "4. اربط الواجهة بوضوح",
    code: "fetch -> state -> component",
    body:
      "في Frontend، اجعل مسار البيانات واضحا: fetch يستدعي endpoint، state يحفظ response، component يعرضها. عند الخطأ، اعرض fallback أو رسالة واضحة، ولا تجعل الشاشة تبدو فارغة.",
    example:
      "مثال: Data Model page تعرض Live Backend API إذا نجح الطلب، وFallback preview إذا لم يعمل Backend.",
  },
  {
    title: "5. أضف اختبارا يحمي المسار",
    code: "tests/test_pipeline.py",
    body:
      "كل ميزة تغير حسابا أو endpoint تحتاج اختبارا صغيرا. الاختبار لا يجب أن يكون ضخما، لكنه يجب أن يثبت أن الحقول الأساسية موجودة وأن response لم ينكسر.",
    example:
      "مثال: إذا أضفت /api/trips/peak، اختبر أن response يحتوي rows وأن كل row يملك trip_id وdeparture_time وfinal_delay_sec.",
  },
  {
    title: "6. وثق أين يظهر الأثر",
    code: "README + page note",
    body:
      "التوثيق المطلوب ليس فقرة عامة. اكتب: أي ملف تغير، أي endpoint يستخدم، أي صفحة تعرض النتيجة، وأي screenshot يثبت أن الميزة تعمل.",
    example:
      "مثال: Feature: Peak filter. Files: backend/main.py, frontend/src/App.jsx. API: GET /api/trips?period=peak. Evidence: screenshot from DSS Workspace.",
  },
];

export const backendDependencies = [
  {
    name: "fastapi",
    usedIn: "backend/main.py",
    why:
      "FastAPI يحول دوال Python إلى HTTP endpoints يمكن للواجهة استدعاؤها. استخدمناه لأن الطالب يحتاج أن يرى بوضوح كيف تصبح الدالة API مثل GET /api/kpis أو GET /api/recommendation.",
    how:
      "كل decorator مثل @app.get('/api/kpis') يحدد route. الدالة ترجع dict أو list، وFastAPI يحولها إلى JSON response يقرأه React.",
  },
  {
    name: "uvicorn[standard]",
    usedIn: "تشغيل Backend محليا",
    why:
      "Uvicorn هو الخادم الذي يشغل FastAPI على الجهاز. بدونه توجد ملفات Python فقط، لكن لا يوجد service يستقبل طلبات من المتصفح.",
    how:
      "الأمر uvicorn backend.main:app --reload يشغل API على http://127.0.0.1:8000. خيار --reload يعيد التشغيل عند تعديل الكود أثناء التعلم.",
  },
  {
    name: "pandas",
    usedIn: "generator.py, analysis.py, scenarios.py, validation.py",
    why:
      "Pandas مناسب لتعليم الجداول: routes وstops وtrips وstop_events. يسمح بالتجميع groupby، حساب المتوسطات، ترتيب القيم، وفحص جودة البيانات بطريقة قريبة من عمل محلل البيانات.",
    how:
      "generator.py ينشئ DataFrames، analysis.py يحسب KPIs، scenarios.py ينسخ stop_events ويعدلها، validation.py يفحص الأعمدة والقيم والعلاقات.",
  },
  {
    name: "pytest",
    usedIn: "tests/test_pipeline.py",
    why:
      "pytest يثبت أن pipeline ما زال يعمل بعد أي تعديل. هذا مهم لأن الطلاب سيغيرون config أو logic وقد يكسرون العلاقات أو الحقول بدون أن ينتبهوا من الواجهة فقط.",
    how:
      "الأمر python -m pytest -q يشغل اختبارات تتأكد من توليد الجداول، جودة البيانات، وجود KPIs، قابلية التوصية للتفسير، وقراءة ملفات repo.",
  },
  {
    name: "nbformat",
    usedIn: "notebooks and future notebook validation",
    why:
      "nbformat يسمح بقراءة ملفات Jupyter Notebook كملفات منظمة. وجوده يهيئ repo لأنشطة تحليلية لاحقة إذا أراد الطلاب ربط notebooks بمخرجات المشروع.",
    how:
      "في هذه النسخة لا يعتمد عليه المسار الرئيسي كثيرا، لكنه موجود حتى تكون بيئة Python جاهزة للتعامل مع notebooks التعليمية عند التوسع.",
  },
];

export const frontendDependencies = [
  {
    name: "react",
    usedIn: "frontend/src/App.jsx",
    why:
      "React يبني الواجهة كمكونات قابلة للقراءة: Dashboard، DataModel، ScenarioLab، RepoStructure. هذا يساعد الطالب على ربط كل جزء من الشاشة بدالة أو component محدد.",
    how:
      "useState يحفظ البيانات المختارة أو نتائج API، وuseEffect يشغل الطلبات عند فتح الصفحة، ثم JSX يحول البيانات إلى cards وtables وsections.",
  },
  {
    name: "react-dom",
    usedIn: "frontend/src/main.jsx",
    why:
      "react-dom يربط React بصفحة HTML الفعلية. هو الجسر بين component tree في JavaScript وDOM الذي يراه المتصفح.",
    how:
      "main.jsx يستخدم createRoot لعرض App داخل عنصر root في index.html.",
  },
  {
    name: "vite",
    usedIn: "npm run dev / npm run build",
    why:
      "Vite يوفر dev server سريع للطلاب ويحول ملفات React وCSS إلى نسخة قابلة للتشغيل في المتصفح. مناسب للتدريب لأن feedback سريع عند تعديل الواجهة.",
    how:
      "npm run dev يشغل الواجهة محليا، وnpm run build يتحقق أن الكود قابل للبناء للإنتاج.",
  },
  {
    name: "lucide-react",
    usedIn: "icons across pages",
    why:
      "الأيقونات تساعد في قراءة النظام بسرعة بدون رسم SVG مخصص لكل زر أو بطاقة. استخدمناها للـAPI، البيانات، الجودة، السيناريو، والملفات.",
    how:
      "يتم import للأيقونة مثل Server أو Database ثم استخدامها كمكون React داخل البطاقات والأزرار.",
  },
];

