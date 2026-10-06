import re
from .normalization import normalize_ar, normalize_en
from .alignment import split_units, aligned_pairs
from .term_provenance import provenance_for

# The challenge appendix explicitly supplies a small starter glossary. Those rows are
# marked ``official`` below. The remaining rows are conservative Mi'yar engineering
# guards: they are intentionally narrow and never presented as an external authority.
# A risky generic equivalent can block publication; an ambiguous/context-dependent
# equivalent asks for review instead of pretending certainty.
TERMS = [
    {
        "ar": "الإسلام", "aliases": ["الإسلام", "اسلام"],
        "accepted": ["islam"], "risky": ["arab culture", "arabic culture"], "review": [],
        "guide": "الإسلام اسم للدين، ولا يختزل في هوية ثقافية أو قومية عامة.",
        "reader_original": "يفهم «الإسلام» اسمًا للدين نفسه.",
        "reader_risky": "قد يفهم المقابل على أنه ثقافة عربية لا دين مستقل.",
        "provenance": "official",
    },
    {
        "ar": "التوحيد", "aliases": ["التوحيد", "توحيد"],
        "accepted": ["tawhid", "tawheed", "oneness of god", "oneness of allah", "worship allah alone", "worship god alone"],
        "risky": ["oneness"], "review": ["monotheism"],
        "guide": "يفضل إبقاء Tawhid أو شرح إفراد الله بالعبادة؛ لا يختزل في مجرد وحدانية عددية.",
        "reader_original": "يفهم «التوحيد» كمفهوم شرعي يتجاوز مجرد الوحدانية العددية.",
        "reader_risky": "قد يفهم المقابل كوحدانية عامة دون الدلالة الشرعية الكاملة.",
        "provenance": "official",
    },
    {
        "ar": "الشريعة", "aliases": ["الشريعة", "شريعة"],
        "accepted": ["sharia", "shariah", "islamic law", "islamic guidance"],
        "risky": ["criminal law", "penal law", "punishments", "criminal code"], "review": [],
        "guide": "تشرح بحسب السياق ولا تختزل في العقوبات أو القانون الجنائي.",
        "reader_original": "يفهم «الشريعة» بوصفها أوسع من جانب العقوبات وحده.",
        "reader_risky": "قد يفهمها كقانون جنائي أو عقوبات فقط.",
        "provenance": "official",
    },
    {
        "ar": "العبادة", "aliases": ["العبادة", "عبادة"],
        "accepted": ["worship", "acts of worship"], "risky": ["ritual", "rituals"], "review": [],
        "guide": "تشمل أعمال القلب والقول والعمل ولا تحصر في الشعائر فقط.",
        "reader_original": "يفهم العبادة بمعناها الشرعي الواسع.",
        "reader_risky": "قد يحصرها في طقوس ظاهرة فقط.",
        "provenance": "official",
    },
    {
        "ar": "النبوة", "aliases": ["النبوة", "نبوة"],
        "accepted": ["prophethood", "prophecy"], "risky": ["religious leadership", "leadership"], "review": [],
        "guide": "تدل على اصطفاء الأنبياء بالوحي، لا مجرد قيادة بشرية.",
        "reader_original": "يفهم النبوة بوصفها اصطفاءً مرتبطًا بالوحي.",
        "reader_risky": "قد يفهمها قيادة دينية بشرية فقط.",
        "provenance": "official",
    },
    {
        "ar": "الوحي", "aliases": ["الوحي", "وحي"],
        "accepted": ["revelation", "divine revelation"], "risky": ["personal inspiration"], "review": ["inspiration"],
        "guide": "المقصود ما أوحاه الله إلى أنبيائه، لا الإلهام الشخصي الفضفاض.",
        "reader_original": "يفهم الوحي بوصفه وحيًا إلهيًا للأنبياء.",
        "reader_risky": "قد يفهمه إلهامًا شخصيًا عامًا.",
        "provenance": "official",
    },
    {
        "ar": "الحديث", "aliases": ["الحديث", "حديث"],
        "accepted": ["hadith", "prophetic tradition"], "risky": ["story", "stories"], "review": [],
        "guide": "ما نقل عن النبي من قول أو فعل أو تقرير ونحو ذلك، مع التحقق من الثبوت عند الاستدلال.",
        "reader_original": "يفهم «الحديث» كمصطلح علمي منقول عن النبي.",
        "reader_risky": "قد يفهمه مجرد قصة أو حكاية.",
        "provenance": "official",
    },
    {
        "ar": "السنة", "aliases": ["السنة", "سنة"],
        "accepted": ["sunnah", "prophetic way", "prophetic practice"], "risky": ["culture", "custom"], "review": ["tradition"],
        "guide": "هدي النبي وطريقته ويحدد المقصود بحسب السياق العلمي.",
        "reader_original": "يفهم السنة بوصفها هدي النبي وطريقته.",
        "reader_risky": "قد يفهمها عادة اجتماعية أو ثقافة بشرية.",
        "provenance": "official",
    },
    {
        "ar": "الفتوى", "aliases": ["الفتوى", "فتوى"],
        "accepted": ["fatwa", "religious ruling"], "risky": ["personal opinion"], "review": ["opinion"],
        "guide": "جواب شرعي يصدره مؤهل في واقعة أو سؤال، ولا يساوى بالمعلومة العامة.",
        "reader_original": "يفهم الفتوى بوصفها جوابًا شرعيًا له شروطه.",
        "reader_risky": "قد يفهمها رأيًا شخصيًا عاديًا.",
        "provenance": "official",
    },
    {
        "ar": "الدعوة", "aliases": ["الدعوة", "دعوة"],
        "accepted": ["da'wah", "dawah", "invitation to islam", "calling to islam"],
        "risky": [], "review": ["mission", "proselytism"],
        "guide": "التعريف بالإسلام والدعوة إليه بالحكمة، ويختار المقابل بحسب السياق والجمهور.",
        "reader_original": "يفهم الدعوة في سياق التعريف بالإسلام والدعوة إليه.",
        "reader_risky": "قد يحمل المقابل إيحاءً أضيق أو مختلفًا بحسب السياق.",
        "provenance": "official",
    },

    # Conservative terminology guards for common high-impact distinctions.
    {
        "ar": "الزكاة", "aliases": ["الزكاة", "زكاة", "زكاه"],
        "accepted": ["Zakat", "zakah", "obligatory almsgiving", "obligatory charity"],
        "risky": ["charity", "donation", "alms", "almsgiving"], "review": [],
        "guide": "الزكاة عبادة مالية واجبة بشروط ومقادير ومصارف مخصوصة؛ لا تساوي مطلق الصدقة أو التبرع.",
        "reader_original": "يفهم «الزكاة» كعبادة مالية واجبة ذات أحكام مخصوصة.",
        "reader_risky": "قد يفهم «charity» أي صدقة أو تبرع اختياري، فتضيع خصوصية الزكاة وإلزامها.",
        "provenance": "curated",
    },
    {
        "ar": "الصدقة", "aliases": ["الصدقة", "صدقة", "صدقه"],
        "accepted": ["sadaqah", "sadaqa", "charity", "charitable giving", "voluntary charity", "almsgiving"],
        "risky": ["zakat", "zakah", "obligatory almsgiving"], "review": [],
        "guide": "الصدقة أوسع من الزكاة، وقد تكون تطوعًا؛ لا تستبدل بالزكاة على أنها الشيء نفسه.",
        "reader_original": "يفهم «الصدقة» بمعناها الأوسع الذي لا يساوي الزكاة الواجبة دائمًا.",
        "reader_risky": "قد يفهمها زكاة واجبة بشروطها الخاصة.",
        "provenance": "curated",
    },
    {
        "ar": "الوضوء", "aliases": ["الوضوء", "وضوء"],
        "accepted": ["wudu", "wudhu", "ablution", "ritual ablution"],
        "risky": ["washing", "washing up", "cleaning"], "review": [],
        "guide": "الوضوء طهارة شرعية مخصوصة، وليس مجرد غسل أو تنظيف عام.",
        "reader_original": "يفهم الوضوء كطهارة شرعية بأفعال مخصوصة.",
        "reader_risky": "قد يفهمه مجرد غسل أو تنظيف.",
        "provenance": "curated",
    },
    {
        "ar": "التيمم", "aliases": ["التيمم", "تيمم"],
        "accepted": ["tayammum", "dry ablution"],
        "risky": ["washing", "cleaning"], "review": ["ablution"],
        "guide": "التيمم طهارة شرعية بديلة لها كيفية مخصوصة، ولا يساوى بالغسل أو الوضوء العادي.",
        "reader_original": "يفهم التيمم كطهارة شرعية بديلة مخصوصة.",
        "reader_risky": "قد يفهمه وضوءًا أو غسلًا عاديًا.",
        "provenance": "curated",
    },
    {
        "ar": "الصيام", "aliases": ["الصيام", "صيام", "الصوم", "صوم"],
        "accepted": ["fasting", "sawm", "fast", "the fast"], "risky": ["dieting", "diet"], "review": ["abstinence"],
        "guide": "الصيام عبادة لها نية وزمن ومفطرات وأحكام؛ لا يختزل في حمية غذائية.",
        "reader_original": "يفهم الصيام كعبادة لها أحكامها.",
        "reader_risky": "قد يفهمه حمية أو امتناعًا عامًا غير تعبدي.",
        "provenance": "curated",
    },
    {
        "ar": "الصمد", "aliases": ["الصمد", "صمد"],
        "accepted": ["the eternal refuge", "eternal refuge", "the self-sufficient", "self-sufficient", "the absolute", "the eternally besought"],
        "risky": ["depends on his creation", "depends on creation", "dependent on creation", "dependent on his creation"], "review": [],
        "guide": "«الصمد» وصف قرآني ذو دلالة مخصوصة؛ لا يحفظها مقابل يجعل الله محتاجًا إلى خلقه أو معتمدًا عليهم.",
        "reader_original": "يفهم وصف «الصمد» ضمن الدلالة القرآنية المنقولة.",
        "reader_risky": "قد يفهم المقابل معنى الاعتماد على الخلق، وهو قلب للدلالة المقصودة في النص.",
        "provenance": "curated",
    },
    {
        "ar": "القيوم", "aliases": ["القيوم", "قيوم"],
        "accepted": ["the sustainer of all existence", "the sustainer", "the self-sustaining", "the all-sustaining", "all-sustaining", "the self-subsisting", "the maintainer of all"],
        "risky": [], "review": [],
        "guide": "«القيوم» يحمل دلالة مستقلة في النص القرآني؛ إسقاطه من الترجمة يحذف جزءًا من المعنى المنقول.",
        "reader_original": "يفهم وصف «القيوم» ضمن المعنى القرآني المنقول.",
        "reader_risky": "قد لا يصل وصف «القيوم» إلى قارئ الترجمة إذا حُذف مقابله.",
        "provenance": "curated", "missing_is_high": True,
    },
    {
        "ar": "الحج", "aliases": ["الحج", "حج"],
        "accepted": ["hajj", "pilgrimage to mecca", "pilgrimage to makkah", "pilgrimage"],
        "risky": ["journey", "travel"], "review": [],
        "guide": "الحج عبادة مخصوصة بمناسك وزمان ومكان، وليس مجرد سفر.",
        "reader_original": "يفهم الحج كعبادة ومناسك مخصوصة.",
        "reader_risky": "قد يفهمه مجرد رحلة أو سفر.",
        "provenance": "curated",
    },
    {
        "ar": "العمرة", "aliases": ["العمرة", "عمرة", "عمره"],
        "accepted": ["umrah", "minor pilgrimage"],
        "risky": ["hajj"], "review": ["pilgrimage"],
        "guide": "العمرة عبادة مستقلة عن الحج؛ استعمال pilgrimage وحدها قد يحتاج تقييدًا بحسب السياق.",
        "reader_original": "يفهم العمرة كنسك مستقل عن الحج.",
        "reader_risky": "قد يخلط القارئ بينها وبين الحج أو أي حج ديني عام.",
        "provenance": "curated",
    },
    {
        "ar": "الربا", "aliases": ["الربا", "ربا"],
        "accepted": ["riba", "usury"],
        "risky": [], "review": ["interest"],
        "guide": "الربا مصطلح فقهي أوسع من مساواته آليًا بكل استعمال لكلمة interest؛ يحتاج المقابل إلى مراعاة السياق الفقهي والمالي.",
        "reader_original": "يفهم الربا كمصطلح فقهي له صور وضوابط.",
        "reader_risky": "قد يفهم المقابل المالي الإنجليزي على نطاق أوسع أو أضيق من المراد الفقهي.",
        "provenance": "curated",
    },
    {
        "ar": "الشرك", "aliases": ["الشرك", "شرك"],
        "accepted": ["shirk", "polytheism", "associating partners with allah", "associating partners with god"],
        "risky": ["atheism"], "review": ["idolatry"],
        "guide": "الشرك لا يساوي الإلحاد، وقد يكون أوسع من حصره في عبادة الأصنام فقط.",
        "reader_original": "يفهم الشرك بمفهومه العقدي الخاص.",
        "reader_risky": "قد يصل معنى آخر مثل الإلحاد أو معنى أضيق من الشرك.",
        "provenance": "curated",
    },
    {
        "ar": "الكفر", "aliases": ["الكفر", "كفر"],
        "accepted": ["kufr", "disbelief", "unbelief"],
        "risky": ["atheism"], "review": [],
        "guide": "الكفر في الاستعمال الشرعي لا يساوي الإلحاد وحده.",
        "reader_original": "يفهم الكفر ضمن دلالته الشرعية بحسب السياق.",
        "reader_risky": "قد يفهمه الإلحاد فقط، وهو أضيق من الاستعمال الشرعي.",
        "provenance": "curated",
    },
    {
        "ar": "التقوى", "aliases": ["التقوى", "تقوى"],
        "accepted": ["taqwa", "god-consciousness", "god consciousness", "piety"],
        "risky": [], "review": ["fear"],
        "guide": "التقوى مفهوم أوسع من الخوف المجرد، ويُشرح بحسب السياق.",
        "reader_original": "يفهم التقوى كمفهوم تعبدي وأخلاقي مركب.",
        "reader_risky": "قد يحصرها المقابل في الخوف النفسي فقط.",
        "provenance": "curated",
    },
    {
        "ar": "الذكر", "aliases": ["الذكر", "ذكر الله"],
        "accepted": ["dhikr", "remembrance of allah", "remembrance of god", "remembrance"],
        "risky": ["meditation"], "review": [],
        "guide": "الذكر عبادة تتعلق بذكر الله، ولا يختزل في التأمل الذهني العام.",
        "reader_original": "يفهم الذكر كعبادة متعلقة بذكر الله.",
        "reader_risky": "قد يفهمه ممارسة تأمل عامة غير مرتبطة بالمعنى الأصلي.",
        "provenance": "curated",
    },
    {
        "ar": "الدعاء", "aliases": ["الدعاء", "دعاء"],
        "accepted": ["dua", "du'a", "supplication", "invocation"],
        "risky": [], "review": ["prayer"],
        "guide": "الدعاء قد يترجم prayer في بعض السياقات، لكن عند احتمال الالتباس مع الصلاة يفضل supplication أو بيان المقصود.",
        "reader_original": "يفهم الدعاء كسؤال الله والتضرع إليه بحسب السياق.",
        "reader_risky": "قد يلتبس عليه المقصود بالصلاة الشعائرية إذا استعمل مقابل عام بلا سياق.",
        "provenance": "curated",
    },
    {
        "ar": "الجهاد", "aliases": ["الجهاد", "جهاد"],
        "accepted": ["jihad"],
        "risky": ["holy war"], "review": ["struggle"],
        "guide": "الجهاد مصطلح شرعي متعدد السياقات؛ لا يختزل آليًا في holy war أو في معنى لغوي عام بلا سياق.",
        "reader_original": "يفهم الجهاد بحسب سياقه الشرعي المحدد.",
        "reader_risky": "قد يحصره المقابل في معنى واحد لا يطابق السياق.",
        "provenance": "curated",
    },
    {
        "ar": "الخمر", "aliases": ["الخمر", "خمر"],
        "accepted": ["intoxicants", "intoxicant", "khamr"],
        "risky": [], "review": ["wine", "alcohol"],
        "guide": "الخمر في الاستعمال الفقهي قد يشمل ما هو أوسع من wine؛ يراعى السياق عند اختيار المقابل.",
        "reader_original": "يفهم المصطلح ضمن الحكم الشرعي المتعلق بالمُسكر.",
        "reader_risky": "قد يحصره المقابل في نوع محدد من الشراب.",
        "provenance": "curated",
    },
    {
        "ar": "الصلاة", "aliases": ["الصلاة", "صلاة", "الصلاه", "صلاه"],
        "accepted": ["salah", "salat", "prayer"], "risky": ["meditation"], "review": ["ritual"],
        "guide": "الصلاة عبادة مخصوصة بأقوال وأفعال معلومة، ولا تختزل في التأمل أو طقس عام.",
        "reader_original": "يفهم الصلاة كعبادة مخصوصة معلومة الأركان والأفعال.",
        "reader_risky": "قد يفهمها ممارسة تأمل أو طقسًا عامًا.", "provenance": "curated",
    },
    {
        "ar": "النية", "aliases": ["النية", "نية", "النيه", "نيه"],
        "accepted": ["intention", "niyyah", "intent"], "risky": ["wish", "desire"], "review": [],
        "guide": "النية قصد القلب للعمل، ولا تساوي مجرد التمني أو الرغبة.",
        "reader_original": "يفهم النية كقصد للعمل.", "reader_risky": "قد يفهمها مجرد أمنية أو رغبة.", "provenance": "curated",
    },
    {
        "ar": "الطهارة", "aliases": ["الطهارة", "طهارة", "الطهاره", "طهاره"],
        "accepted": ["taharah", "ritual purity", "purification"], "risky": [], "review": ["cleanliness", "hygiene"],
        "guide": "الطهارة في السياق الفقهي أوسع من النظافة الحسية وحدها.",
        "reader_original": "يفهم الطهارة ضمن معناها الشرعي المتعلق برفع الحدث وإزالة النجاسة بحسب السياق.", "reader_risky": "قد يحصرها في النظافة أو الصحة العامة.", "provenance": "curated",
    },
    {
        "ar": "الغسل", "aliases": ["الغسل", "غسل"],
        "accepted": ["ghusl", "ritual bath", "full ritual bath"], "risky": [], "review": ["shower", "bath"],
        "guide": "الغسل الشرعي عبادة طهارة مخصوصة، وقد لا يكفي وصفه بدش أو حمام عادي دون سياق.",
        "reader_original": "يفهم الغسل كطهارة شرعية مخصوصة.", "reader_risky": "قد يفهمه استحمامًا اعتياديًا فقط.", "provenance": "curated",
    },
    {
        "ar": "القبلة", "aliases": ["القبلة", "قبلة", "القبله", "قبله"],
        "accepted": ["qibla", "qiblah", "direction of prayer", "prayer direction"], "risky": ["east", "eastern direction"], "review": [],
        "guide": "القبلة هي جهة الكعبة للصلاة، ولا تساوي جهة الشرق على إطلاقها.",
        "reader_original": "يفهم القبلة كجهة الكعبة في الصلاة.", "reader_risky": "قد يفهمها اتجاه الشرق دائمًا، وهو غير صحيح مكانيًا.", "provenance": "curated",
    },
    {
        "ar": "الأذان", "aliases": ["الأذان", "اذان", "الأذان"],
        "accepted": ["adhan", "azan", "call to prayer"], "risky": ["announcement"], "review": [],
        "guide": "الأذان نداء مخصوص للصلاة بألفاظ معلومة، وليس إعلانًا عامًا.",
        "reader_original": "يفهم الأذان كنداء مخصوص للصلاة.", "reader_risky": "قد يفهمه مجرد إعلان.", "provenance": "curated",
    },
    {
        "ar": "الركوع", "aliases": ["الركوع", "ركوع"],
        "accepted": ["ruku", "ruku'", "bowing"], "risky": ["kneeling"], "review": [],
        "guide": "الركوع انحناء مخصوص في الصلاة، وليس هو الركوع على الركبتين أو السجود.",
        "reader_original": "يفهم الركوع كهيئة الانحناء المخصوصة في الصلاة.", "reader_risky": "قد يفهمه kneeling وهي هيئة أخرى.", "provenance": "curated",
    },
    {
        "ar": "السجود", "aliases": ["السجود", "سجود"],
        "accepted": ["sujud", "prostration"], "risky": ["kneeling", "bowing"], "review": [],
        "guide": "السجود هيئة مخصوصة تختلف عن الركوع أو مجرد الجثو على الركبتين.",
        "reader_original": "يفهم السجود كهيئة السجود المخصوصة.", "reader_risky": "قد يخلطه بالركوع أو kneeling.", "provenance": "curated",
    },
    {
        "ar": "الإحرام", "aliases": ["الإحرام", "احرام"],
        "accepted": ["ihram", "state of ihram", "state of consecration"], "risky": ["white clothes", "white clothing"], "review": [],
        "guide": "الإحرام حالة نسك ومحظورات، وليس مجرد لبس الثياب البيضاء.",
        "reader_original": "يفهم الإحرام كدخول في حالة النسك بأحكامها.", "reader_risky": "قد يفهمه مجرد لباس أبيض.", "provenance": "curated",
    },
    {
        "ar": "الكفارة", "aliases": ["الكفارة", "كفارة", "الكفاره", "كفاره"],
        "accepted": ["kaffarah", "expiation"], "risky": [], "review": ["fine", "penalty"],
        "guide": "الكفارة عبادة أو التزام شرعي لجبر مخالفة مخصوصة، ولا تساوي غرامة قانونية عامة.",
        "reader_original": "يفهم الكفارة بوصفها حكمًا شرعيًا مخصوصًا.", "reader_risky": "قد يفهمها غرامة أو عقوبة مالية عامة.", "provenance": "curated",
    },
    {
        "ar": "الوقف", "aliases": ["الوقف", "وقف"],
        "accepted": ["waqf", "endowment", "charitable endowment"], "risky": ["donation"], "review": [],
        "guide": "الوقف حبس أصل وتسبيل منفعة وفق أحكام مخصوصة، وليس تبرعًا عابرًا فقط.",
        "reader_original": "يفهم الوقف كترتيب مستمر له أحكامه.", "reader_risky": "قد يفهمه تبرعًا عاديًا ينتهي بتسليم المال.", "provenance": "curated",
    },
    {
        "ar": "العدة", "aliases": ["العدة", "عدة", "العده", "عده"],
        "accepted": ["iddah", "waiting period"], "risky": [], "review": ["divorce period"],
        "guide": "العدة مدة شرعية لها أسباب وأحكام متعددة، فلا تحصر دائمًا في الطلاق فقط.",
        "reader_original": "يفهم العدة كمدة شرعية بحسب سببها.", "reader_risky": "قد يحصرها في حالة الطلاق فقط.", "provenance": "curated",
    },
    {
        "ar": "الحجاب", "aliases": ["الحجاب", "حجاب"],
        "accepted": ["hijab", "islamic veil"], "risky": [], "review": ["headscarf", "veil"],
        "guide": "الحجاب في السياق الشرعي قد يدل على معنى أوسع من قطعة لباس واحدة؛ يراعى السياق ولا يختزل آليًا في غطاء الرأس فقط.",
        "reader_original": "يفهم الحجاب وفق السياق الشرعي المقصود.", "reader_risky": "قد يحصر المقابل المعنى في قطعة لباس واحدة دون بقية السياق.", "provenance": "curated",
    },
    {
        "ar": "العورة", "aliases": ["العورة", "عورة", "العوره", "عوره"],
        "accepted": ["awrah", "parts that must be covered", "parts of the body that must be covered"], "risky": ["genitals"], "review": ["private parts"],
        "guide": "العورة مصطلح فقهي يتغير نطاقه بحسب السياق، ولا يساوي الأعضاء التناسلية فقط.",
        "reader_original": "يفهم العورة كنطاق فقهي لما يجب ستره بحسب السياق.", "reader_risky": "قد يحصرها في الأعضاء التناسلية فقط.", "provenance": "curated",
    },
    {
        "ar": "النكاح", "aliases": ["النكاح", "نكاح"],
        "accepted": ["nikah", "marriage", "marriage contract"], "risky": ["sex", "sexual intercourse"], "review": [],
        "guide": "النكاح في السياق الفقهي يدل على الزواج وعقده، ولا يساوى بالعلاقة الجنسية وحدها.",
        "reader_original": "يفهم النكاح بوصفه زواجًا أو عقد زواج بحسب السياق.", "reader_risky": "قد يفهمه علاقة جنسية فقط، وهو تغيير جوهري في الدلالة.", "provenance": "curated",
    },
    {
        "ar": "المهر", "aliases": ["المهر", "مهر", "الصداق", "صداق"],
        "accepted": ["mahr", "dower", "bridal gift"], "risky": [], "review": ["dowry"],
        "guide": "المهر حق مالي للزوجة، واستعمال dowry قد يلتبس بعادات مالية مختلفة بين الثقافات.",
        "reader_original": "يفهم المهر كحق مالي للزوجة في عقد الزواج.", "reader_risky": "قد يفهم المقابل نظامًا ماليًا ثقافيًا مختلفًا عن المهر.", "provenance": "curated",
    },
    {
        "ar": "الإيمان", "aliases": ["الإيمان", "ايمان"],
        "accepted": ["iman", "faith"], "risky": [], "review": ["belief"],
        "guide": "الإيمان مصطلح شرعي مركب، وقد يكون belief مناسبًا في بعض السياقات لكنه يحتاج ضبطًا حين يراد المعنى الاصطلاحي الكامل.",
        "reader_original": "يفهم الإيمان بمعناه الشرعي بحسب السياق.", "reader_risky": "قد يصل معنى اعتقاد ذهني عام دون بقية الدلالة الاصطلاحية.", "provenance": "curated",
    },
    {
        "ar": "القدر", "aliases": ["القدر", "قدر الله"],
        "accepted": ["qadar", "divine decree", "predestination"], "risky": [], "review": ["fate", "destiny"],
        "guide": "القدر مفهوم عقدي يتعلق بتقدير الله، ولا يختزل في تصور ثقافي عام عن الحظ أو المصير.",
        "reader_original": "يفهم القدر ضمن مفهومه العقدي.", "reader_risky": "قد يفهمه مصيرًا غامضًا أو حظًا خارج الدلالة العقدية.", "provenance": "curated",
    },
    {
        "ar": "البدعة", "aliases": ["البدعة", "بدعة", "البدعه", "بدعه"],
        "accepted": ["bid'ah", "bidah", "religious innovation"], "risky": [], "review": ["innovation"],
        "guide": "البدعة في السياق الشرعي مصطلح ديني، وكلمة innovation العامة قد تكون أوسع من المراد.",
        "reader_original": "يفهم البدعة كمصطلح ديني بحسب السياق.", "reader_risky": "قد يفهمها أي ابتكار جديد ولو كان تقنيًا أو دنيويًا.", "provenance": "curated",
    },
    {
        "ar": "التوبة", "aliases": ["التوبة", "توبة", "التوبه", "توبه"],
        "accepted": ["repentance", "tawbah", "tawba"], "risky": [], "review": ["regret"],
        "guide": "التوبة أوسع من مجرد الندم؛ تتضمن الرجوع عن الذنب وما يتصل بها من شروط بحسب الحال.",
        "reader_original": "يفهم التوبة كرجوع عن الذنب إلى الله.", "reader_risky": "قد يفهمها شعور ندم فقط دون معنى الرجوع والتوبة.", "provenance": "curated",
    },
    {
        "ar": "الاستغفار", "aliases": ["الاستغفار", "استغفار"],
        "accepted": ["seeking forgiveness", "istighfar", "asking allah for forgiveness", "asking god for forgiveness"], "risky": ["apology"], "review": [],
        "guide": "الاستغفار طلب المغفرة من الله، ولا يساوى باعتذار بشري عام.",
        "reader_original": "يفهم الاستغفار كطلب مغفرة الله.", "reader_risky": "قد يفهمه مجرد تقديم اعتذار لشخص آخر.", "provenance": "curated",
    },
    {
        "ar": "الشهيد", "aliases": ["الشهيد", "شهيد"],
        "accepted": ["martyr", "shaheed", "shahid"], "risky": [], "review": ["victim"],
        "guide": "الشهيد مصطلح شرعي لا يساوى آليًا بكل ضحية؛ يراعى السياق ولا يُحكم لأشخاص معينين بلا مستند.",
        "reader_original": "يفهم المصطلح ضمن دلالته الشرعية أو الوصفية بحسب السياق.", "reader_risky": "قد يتحول المعنى إلى مجرد ضحية أو إلى حكم قطعي على شخص بعينه.", "provenance": "curated",
    },

]


def _ar_matches(ar_text: str, aliases):
    """Return de-duplicated Arabic term occurrences.

    A document can contain the same sensitive term more than once. Counting the
    occurrences prevents one correct equivalent from masking a later inaccurate
    rendering in a long passage.
    """
    hits=[]; seen=set()
    for alias in sorted(aliases, key=len, reverse=True):
        a=normalize_ar(alias)
        if not a:
            continue
        # Arabic conjunctions are commonly attached orthographically: والزكاة، فالصلاة.
        pat=rf"(?<![\u0600-\u06FF])(?:و|ف)?{re.escape(a)}(?![\u0600-\u06FF])"
        for m in re.finditer(pat, ar_text):
            span=(m.start(),m.end())
            # Do not double-count an alias contained in a longer alias already seen.
            if any(c <= span[0] and span[1] <= d for c,d in seen):
                continue
            seen.add(span)
            hits.append({"phrase":alias,"span":span})
    return sorted(hits,key=lambda x:x["span"][0])


def _en_matches(en_text: str, phrases):
    """Return every de-duplicated English phrase match, longest phrase first."""
    hits=[]; seen=set()
    for phrase in sorted(phrases,key=len,reverse=True):
        p=normalize_en(phrase)
        if not p:
            continue
        for m in re.finditer(rf"(?<![a-z]){re.escape(p)}(?![a-z])",en_text):
            span=(m.start(),m.end())
            if any(c <= span[0] and span[1] <= d for c,d in seen):
                continue
            seen.add(span)
            hits.append({"phrase":phrase,"span":span})
    return sorted(hits,key=lambda x:x["span"][0])


def _covered(inner, outer):
    if not inner or not outer:
        return False
    a,b=inner["span"]; c,d=outer["span"]
    return c <= a and b <= d


def _definition_link(en_text: str, accepted_hits, other_hits):
    """Detect an explicit gloss that defines a preserved term too narrowly.

    Example: ``Sharia is criminal law`` must still be flagged even though the
    transliteration ``Sharia`` itself is present. By contrast, in ``Zakat is
    obligatory and charity is recommended`` the word ``charity`` belongs to a
    different concept and must not contaminate the Zakat check.
    """
    link=re.compile(r"^[\s,:;()\-]*(?:is|(?:simply\s+)?means(?:\s+(?:general|mere|ordinary))?|meaning|refers\s+to|i\.?e\.?|that\s+is|is\s+merely|is\s+only|means\s+merely|means\s+only)(?:\s+(?:a|an|the))?[\s,:;()\-]*$",re.I)
    for a in accepted_hits:
        for o in other_hits:
            if o["span"][0] < a["span"][1]:
                continue
            between=en_text[a["span"][1]:o["span"][0]]
            if len(between) <= 55 and link.fullmatch(between):
                return o
    return None


def _split_units(text):
    return split_units(text)


def _term_applicable(t, original_text):
    """Guard lexical homographs that are not necessarily religious terms.

    Bare «غسل» often means ordinary washing or is a verb. Treat it as the ritual
    purification term only when the definite noun, explicit damma form, or religious
    purification context is present.
    """
    if t.get("ar") != "الغسل":
        return True
    raw=original_text or ""
    norm=normalize_ar(raw)
    if re.search(r"(?:^|\s)الغسل(?:$|[\s،,.؛!?؟])", norm):
        return True
    if re.search(r"غُس(?:ْ)?ل", raw):
        return True
    religious=bool(re.search(r"(?:الجنابة|جنابة|الحيض|النفاس|الطهارة|يتطهر|طهارة)", norm))
    return religious


def _nearest_occurrence(ar_hit, ar_text, en_hits, en_text):
    """Choose the English occurrence that best corresponds to an Arabic occurrence.

    Long clauses can contain the same English surface form for different Arabic terms
    (e.g. صدقة ... زكاة -> charity ... charity).  Choosing the first occurrence
    globally is unsafe, so align by relative position inside the already-aligned unit.
    """
    if not en_hits:
        return None
    amid=(ar_hit["span"][0]+ar_hit["span"][1])/2
    ar_ratio=amid/max(1,len(ar_text))
    def score(hit):
        emid=(hit["span"][0]+hit["span"][1])/2
        return abs((emid/max(1,len(en_text)))-ar_ratio)
    return min(en_hits,key=score)


def _term_pair_result(t, ar, en, segment_index=None):
    """Evaluate one Arabic/English unit for one sensitive term."""
    ar_hits=_ar_matches(ar,t.get("aliases") or [t["ar"]])
    if not ar_hits:
        return [],[]
    accepted_hits=_en_matches(en,t.get("accepted",[]))
    risky_hits=_en_matches(en,t.get("risky",[]))
    review_hits=_en_matches(en,t.get("review",[]))
    risky_hits=[r for r in risky_hits if not any(_covered(r,a) for a in accepted_hits)]
    review_hits=[r for r in review_hits if not any(_covered(r,a) for a in accepted_hits)]
    ar_count=len(ar_hits); accepted_count=len(accepted_hits)
    # Context bridge: when «الطهارة» is used to define الوضوء, a precise Wudu/ritual-ablution
    # rendering can preserve the proposition without repeating the broader noun "purification".
    if t.get("ar")=="الطهارة" and re.search(r"(?<![\u0600-\u06FF])(?:و|ف)?(?:ال)?وضوء(?![\u0600-\u06FF])", ar):
        if re.search(r"\b(?:wudu|wudhu|ritual ablution|ablution)\b", en):
            accepted_count=max(accepted_count,ar_count)
    missing=max(0,ar_count-accepted_count)
    defining_risky=_definition_link(en,accepted_hits,risky_hits)
    defining_review=_definition_link(en,accepted_hits,review_hits)
    # When the same rendering occurs more than once in one unit, bind the warning
    # to the occurrence nearest the Arabic term instead of blindly taking the first.
    anchor_ar = ar_hits[min(max(accepted_count, 0), len(ar_hits)-1)] if ar_hits else None
    positional_risky = _nearest_occurrence(anchor_ar, ar, risky_hits, en) if (missing and anchor_ar) else None
    positional_review = _nearest_occurrence(anchor_ar, ar, review_hits, en) if (missing and anchor_ar) else None
    risky=defining_risky or positional_risky
    review=None if risky else (defining_review or positional_review)

    official=t.get("provenance")=="official"
    evidence_kind="official_glossary_guideline" if official else "curated_terminology_rule"
    suffix=f" — المقطع {segment_index}" if segment_index is not None else ""
    meta={"segment_index":segment_index} if segment_index is not None else {}
    checks=[]; issues=[]
    if risky:
        checks.append({"check":f"مصطلح {t['ar']}{suffix}","status":"fail","detail":"مقابل عام أو مختلف قد يغيّر الدلالة الاصطلاحية"})
        issues.append({
            "type":"flattening","severity":"high","title":f"ترجمة غير دقيقة لمصطلح «{t['ar']}»{suffix}",
            "explanation_ar":f"المقابل «{risky['phrase']}» لا يحفظ الدلالة الاصطلاحية الكاملة لـ«{t['ar']}» في هذا السياق.",
            "impact_ar":t["guide"],"confidence":0.93 if official else 0.90,"evidence_kind":evidence_kind,
            "source_span":t["ar"],"translation_span":risky["phrase"],"reader_original":t.get("reader_original"),
            "reader_translation":t.get("reader_risky"),"gap_ar":t["guide"],"source_count":ar_count,
            "accepted_translation_count":accepted_count,
            "translation_local_span":list(risky["span"]) if risky else None,
            "translation_occurrence_index":(1 + sum(1 for h in risky_hits if h["phrase"].lower()==risky["phrase"].lower() and h["span"][0] < risky["span"][0])) if risky else None,
            **meta,
        })
        return issues,checks
    if review:
        checks.append({"check":f"مصطلح {t['ar']}{suffix}","status":"review","detail":"المقابل محتمل لكنه يعتمد على السياق"})
        issues.append({
            "type":"terminology","severity":"medium","title":f"مقابل يحتاج مراجعة لمصطلح «{t['ar']}»{suffix}",
            "explanation_ar":f"المقابل «{review['phrase']}» قد يكون مناسبًا في بعض السياقات، لكنه لا يكفي وحده لإثبات حفظ الدلالة الاصطلاحية.",
            "impact_ar":t["guide"],"confidence":0.76,"evidence_kind":evidence_kind,"source_span":t["ar"],
            "translation_span":review["phrase"],"reader_original":t.get("reader_original"),
            "reader_translation":t.get("reader_risky"),"gap_ar":t["guide"],**meta,
        })
        return issues,checks
    if accepted_count>=ar_count:
        shown=accepted_hits[0]["phrase"] if accepted_hits else "مقابل معتمد"
        checks.append({"check":f"مصطلح {t['ar']}{suffix}","status":"pass","detail":f"المقابل ظاهر بما يغطي المواضع المكتشفة: {shown}"})
        return issues,checks
    if t.get("missing_is_high"):
        checks.append({"check":f"مصطلح {t['ar']}{suffix}","status":"fail","detail":"المعنى الاصطلاحي الظاهر في الأصل مفقود من الترجمة"})
        issues.append({
            "type":"omission","severity":"high","title":f"فقدان دلالة «{t['ar']}»{suffix}",
            "explanation_ar":f"ظهر «{t['ar']}» في الأصل دون مقابل واضح في الترجمة.",
            "impact_ar":t["guide"],"confidence":0.91,"evidence_kind":evidence_kind,"source_span":t["ar"],
            "translation_span":"لا يوجد مقابل واضح","reader_original":t.get("reader_original"),
            "reader_translation":t.get("reader_risky") or "قد لا يصل هذا الجزء من المعنى إلى قارئ الترجمة.",
            "gap_ar":t["guide"],**meta,
        })
    else:
        # A dictionary miss is not itself a semantic defect.  Keep it as internal
        # review evidence only; a user-facing terminology finding requires an aligned
        # target span (risky/review rendering) or an explicitly high-risk omission.
        checks.append({"check":f"مصطلح {t['ar']}{suffix}","status":"review","detail":"UNCERTAIN_TERMINOLOGY_EVIDENCE: لا يوجد مقابل محلي محسوم؛ لا تُنشأ فجوة نهائية بلا span مترجم."})
    return issues,checks


def analyze_terminology(ar_text, en_text):
    ar,en=normalize_ar(ar_text),normalize_en(en_text)
    issues=[]; checks=[]; evidence=[]
    pairs,align_mode=aligned_pairs(ar_text,en_text)

    for t in TERMS:
        # Add provenance evidence only when the Arabic term actually occurs anywhere.
        if not _term_applicable(t, ar_text) or not _ar_matches(ar,t.get("aliases") or [t["ar"]]):
            continue
        official=t.get("provenance")=="official"
        prov=provenance_for(t["ar"]) or {}
        refs=prov.get("source_refs") or []
        basis="، ".join(r.get("name","") for r in refs[:2] if r.get("name"))
        detail=t["guide"] + ((" | الأساس المرجعي: "+basis) if basis else "")
        evidence.append({
            "source":"الحزمة العلمية للتحدي — نماذج قاموس المصطلحات" if official else "قاموس مِعيار المصطلحي — قاعدة محافظة موثقة الأساس",
            "title":t["ar"],"detail":detail,
            "status":"local_verified_guideline" if official else "local_curated_rule",
            "evidence_type":"terminology_guideline",
            "source_basis":refs,
            "grounding_status":prov.get("grounding_status"),
            "policy_note":prov.get("policy_note"),
        })

        # «القيوم» commonly occurs inside a long Qur'anic verse whose punctuation
        # can split Arabic/English clauses differently.  When it occurs exactly once
        # and a recognized accepted rendering is present globally, bind that rendering
        # before sentence-local alignment so punctuation cannot create a false omission.
        global_ar_hits=_ar_matches(ar,t.get("aliases") or [t["ar"]])
        global_acc_hits=_en_matches(en,t.get("accepted",[]))
        if t.get("ar")=="القيوم" and len(global_ar_hits)==1 and global_acc_hits:
            ii,cc=_term_pair_result(t,ar,en,None)
            issues.extend(ii); checks.extend(cc)
            continue

        if len(pairs)>1:
            # Sentence/chunk-local matching prevents a correct equivalent elsewhere
            # from masking a bad rendering here, even when punctuation counts differ.
            for idx,ars,ens in pairs:
                arn=normalize_ar(ars)
                if not _term_applicable(t, ars) or not _ar_matches(arn,t.get("aliases") or [t["ar"]]):
                    continue
                ii,cc=_term_pair_result(t,arn,normalize_en(ens),idx)
                issues.extend(ii); checks.extend(cc)
        else:
            ii,cc=_term_pair_result(t,ar,en,None)
            issues.extend(ii); checks.extend(cc)

    return {"issues":issues,"checks":checks,"evidence":evidence}
