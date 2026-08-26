export const pageCopy = {
  problem: {
    ar: "صياغة المشكلة",
    label: "Problem Statement",
    role: "Framing",
    description:
      "نبدأ من المشكلة قبل القرار: أين يظهر تأخر الحافلات، من يتأثر به، ولماذا لا يكفي أن نقول إن هناك تأخيرا عاما دون تحديد أثره التشغيلي وثقة الجمهور.",
  },
  canvas: {
    ar: "مدخل المشروع",
    label: "Project Entry",
    role: "Guide",
    description:
      "صفحة البداية التي تشرح لماذا يوجد هذا repo، ما الذي يبنيه فريق B، وكيف تتحرك الرحلة من المشكلة إلى بيانات وBackend وFrontend وتوصية قابلة للمراجعة.",
  },
  overview: {
    ar: "تعريف القرار",
    label: "Decision Brief",
    role: "Decision",
    description:
      "تبدأ رحلة DSS من القرار المطلوب دعمه: من صاحب القرار، ما المشكلة التشغيلية، وما الدليل الذي يجعل التوصية قابلة للمراجعة.",
  },
  model: {
    ar: "نموذج البيانات",
    label: "Data Model",
    role: "Data",
    description:
      "شرح الجداول والعلاقات وماذا يمثّل الصف الواحد؟ قبل تحويل البيانات إلى مؤشرات أو توصيات.",
  },
  lab: {
    ar: "مختبر توليد البيانات",
    label: "Synthetic Data Lab",
    role: "Data",
    description:
      "مساحة لفهم كيف تتحول قواعد config إلى Training Data قابلة للفحص والمقارنة.",
  },
  quality: {
    ar: "فحص جودة البيانات",
    label: "Data Quality Gate",
    role: "Gate",
    description:
      "لا ينتقل النظام إلى التحليل أو التوصية قبل فحص جودة البيانات. هذه الصفحة تشرح ما الذي يجب أن ينجح ولماذا.",
  },
  dashboard: {
    ar: "لوحة أداء المسار",
    label: "Route Performance",
    role: "Analysis",
    description:
      "اللوحة التشغيلية الأساسية: قراءة الحالة، تحديد الأولوية، مقارنة المؤشرات، والوصول إلى الحالة التي تستحق التدخل.",
  },
  explorer: {
    ar: "دليل التأخير",
    label: "Delay Evidence",
    role: "Evidence",
    description:
      "تفكيك الأرقام: أين ظهر التأخير، ما المحطة المتأثرة، وما الدليل الذي يدعم أي ادعاء في العرض النهائي.",
  },
  scenario: {
    ar: "مختبر التدخلات",
    label: "Scenario Lab",
    role: "Experiment",
    description:
      "مقارنة تدخلات محتملة قبل تنفيذها، وفهم كيف تتغير الثقة والتحسن المتوقع وAction Score.",
  },
  recommendation: {
    ar: "التوصية والقرار",
    label: "Decision Recommendation",
    role: "Decision",
    description:
      "تحويل التحليل إلى توصية قابلة للمراجعة مع الدليل، الثقة، القيود، والخطوة التالية.",
  },
  governance: {
    ar: "مراجعة الحوكمة والمخاطر",
    label: "Governance & Risk Review",
    role: "Review",
    description:
      "صفحة نموذجية تساعد الطالب على شرح مخاطر المشروع وحدود البيانات والامتثال والحوكمة بدون الادعاء أن النظام يفرض GRC تقنيا.",
  },
  tasks: {
    ar: "خارطة بناء المنتج",
    label: "Build Roadmap",
    role: "Plan",
    description:
      "خطة تنفيذ تعليمية مرتبة بالأسبوع: ماذا ينجز الطالب، أين يعيش العمل داخل repo، وأي دليل يثبت أن المهمة اكتملت.",
  },
  walkthrough: {
    ar: "مراجعة الكود",
    label: "Code Walkthrough",
    role: "Code",
    description:
      "مسار قراءة بدون كتابة: يمر الطالب على محطات تقنية ويفهم ماذا يفتح، ماذا يتتبع، وما الذي يجب أن يستطيع شرحه شفهيا.",
  },
  featureflow: {
    ar: "إضافة ميزة",
    label: "Add a Feature",
    role: "Dev",
    description:
      "شرح كيف يتحول طلب ميزة في Frontend إلى API contract وتعديل Backend وtests وواجهة ودليل مراجعة.",
  },
  kpi: {
    ar: "بناء KPI",
    label: "KPI Builder",
    role: "Metric",
    description:
      "تعلم كيف يولد KPI من سؤال تشغيلي، جدول مصدر، حقول، formula، threshold، ثم يظهر في Dashboard ويدعم قرارا محددا.",
  },
  structure: {
    ar: "ملفات المشروع",
    label: "Project Files",
    role: "Repo",
    description:
      "ربط كل ملف بدوره في المنتج حتى يعرف الطالب أين يقرأ، أين يعدل، وأين يجمع الدليل.",
  },
};

export const navigationSections = [
  {
    title: "خطوات مشروع المدينة الذكية",
    label: "Smart City Project Steps",
    numbered: true,
    pages: ["problem", "overview", "model", "lab", "quality", "dashboard", "explorer", "scenario", "recommendation", "governance"],
  },
  {
    title: "دليل بناء المنتج",
    label: "Build Guidance",
    pages: ["canvas", "tasks", "walkthrough", "featureflow", "structure", "kpi"],
  },
];

export const navigationOrder = navigationSections.flatMap((section) => section.pages);
