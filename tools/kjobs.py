import json
U='https://www.tal83.com/img/'
PH={
 'k01':[U+'bucket-crane-petah-tikva.jpg',U+'truck-street.jpg',U+'crane-basket-safety-tip-power-lines.jpg',U+'hero-boom.jpg'],
 'k02':['assets/diag/tm.png',U+'hero-boom.jpg',U+'truck-street.jpg'],
 'k03':['assets/diag/jib.png',U+'boom-towers.jpg',U+'hero-boom.jpg'],
 'k04':['assets/diag/angle.png',U+'hero-boom.jpg',U+'bucket-crane-petah-tikva.jpg'],
 'k05':['assets/diag/mobile.png',U+'boom-towers.jpg','assets/diag/tm.png'],
 'k06':['assets/diag/platforms.png',U+'aerial-lift-rental-shoham.jpg',U+'boom-lift-rental-yehud.jpg'],
}
V={'he':'he-IL-AvriNeural','ar':'ar-SA-HamedNeural','ru':'ru-RU-DmitryNeural','en':'en-US-GuyNeural','fr':'fr-FR-HenriNeural'}
T={
'he':{
 'k01':('מה זה מנוף סל?',['מנוף סל זה מנוף זרוע על משאית, עם סל לאדם בקצה.','אותו מנוף שמוריד דוד שמש, מרים גם את המתקין לשלט בקומה רביעית.','מודדים גובה ומרחק מהמדרכה, לא מהקיר, ומוסיפים שלושה עד ארבעה מטר ביטחון.','בודקים חוטי חשמל, מקום לתמיכות, ומשטח שלא שוקע.','המדריך המלא באתר טל שמונים ושלוש נקודה קום.']),
 'k02':('טון-מטר: למה רחוק מרים פחות?',['מנוף זרוע נמדד בטון-מטר: משקל כפול מרחק.','מנוף של שתים עשרה טון-מטר, בתיאוריה מרים ארבעה טון בשלושה מטר.','אבל בשתים עשרה מטר? רק בערך טון אחד.','ובפועל עוד פחות, כי גם הזרוע עצמה שוקלת.','מה שקובע זו רק טבלת העומסים של היצרן.']),
 'k03':('מה זה ג׳יב במנוף?',['ג׳יב זו זרוע נוספת שמתחברת לקצה הזרוע.','הוא מוסיף גובה וטווח, ומגיע מעל קיר ומסביב למכשולים.','המחיר: בקצה הג׳יב מרימים פחות.','וגם המשקל של הג׳יב עצמו נחשב חלק מהעומס.','עם ג׳יב או בלי? תלוי בעבודה. שואלים לפני.']),
 'k04':('זווית הזרוע – הסוד של המנופאי',['זרוע זקופה מקרבת את המטען, ומרימים יותר.','זרוע שטוחה מרחיקה את המטען, ומרימים פחות.','המרחק האופקי הוא אורך הזרוע כפול קוסינוס הזווית.','מחוגת הזווית על הזרוע אומרת למנופאי איפה הוא עומד.','ואם הזווית לא מופיעה בטבלה, לוקחים את הנמוכה הבאה.']),
 'k05':('עגורן 100 טון מרים 100 טון?',['לא בדיוק.','המספר בשם העגורן הוא הכושר ברדיוס הכי קצר, עם תמיכות פתוחות.','ככל שהמטען מתרחק, הכושר יורד מאוד.','היתרון של עגורן גדול הוא המרחק והגובה.','לכן בכל הרמה גדולה: טבלת יצרן ותוכנית הרמה.']),
 'k06':('במות הרמה – איזו מתאימה לכם?',['במת מספריים עולה ישר למעלה, עם משטח רחב.','במה מפרקית מגיעה מעל ומסביב למכשולים.','במה טלסקופית מתאימה לגובה ולמרחק בשטח פתוח.','בבמה, מי שעומד למעלה שולט בה. במנוף סל, המנופאי מלמטה.','ובכל מקרה: תסקיר בתוקף, והדרכת עבודה בגובה.']),
},
'ar':{
 'k01':('ما هي رافعة السلة؟',['رافعة السلة هي رافعة ذراع على شاحنة، وفي طرفها سلة لشخص.','نفس الرافعة التي تنزل سخان الماء، ترفع أيضاً عامل تركيب اللافتات للطابق الرابع.','نقيس الارتفاع والمسافة من الرصيف، وليس من الحائط، ونضيف ثلاثة إلى أربعة أمتار للأمان.','نفحص أسلاك الكهرباء، ومكان الأرجل الداعمة، وأرضاً لا تغوص.','الدليل الكامل على موقع tal83.com']),
 'k02':('طن-متر: لماذا ترفع أقل كلما ابتعدت؟',['تُقاس رافعة الذراع بالطن-متر: الوزن مضروباً في المسافة.','رافعة ١٢ طن-متر ترفع نظرياً أربعة أطنان على بعد ثلاثة أمتار.','لكن على بعد ١٢ متراً؟ حوالي طن واحد فقط.','وفي الواقع أقل، لأن الذراع نفسها لها وزن.','الحكم الوحيد هو جدول الأحمال من الشركة المصنعة.']),
 'k03':('ما هو الجيب في الرافعة؟',['الجيب ذراع إضافية تُركّب في طرف الذراع الرئيسية.','تضيف ارتفاعاً ومدى، وتصل فوق الجدار وحول العوائق.','الثمن: في طرف الجيب نرفع أقل.','ووزن الجيب نفسه يُحسب من الحمل.','مع جيب أو بدون؟ حسب العمل، اسألوا قبل.']),
 'k04':('زاوية الذراع – سر عامل الرافعة',['الذراع العمودية تقرّب الحمل، فنرفع أكثر.','الذراع المنبسطة تبعد الحمل، فنرفع أقل.','المسافة الأفقية هي طول الذراع ضرب جيب تمام الزاوية.','مؤشر الزاوية على الذراع يخبر المشغّل أين هو.','وإذا لم تكن الزاوية في الجدول، نأخذ الأقل التالية.']),
 'k05':('رافعة ١٠٠ طن ترفع ١٠٠ طن؟',['ليس تماماً.','الرقم في اسم الرافعة هو القدرة في أقصر نصف قطر، مع أرجل مفتوحة.','كلما ابتعد الحمل، تنخفض القدرة كثيراً.','ميزة الرافعة الكبيرة هي المسافة والارتفاع.','لذلك في كل رفع كبير: جدول المصنع وخطة رفع.']),
 'k06':('منصات الرفع – أيها يناسبكم؟',['المنصة المقصية ترتفع للأعلى مباشرة، بسطح واسع.','المنصة المفصلية تصل فوق العوائق وحولها.','المنصة التلسكوبية للارتفاع والمسافة في مكان مفتوح.','في المنصة، من يقف فوق يتحكم بها. في رافعة السلة، المشغل من تحت.','وفي كل حال: فحص ساري المفعول وتدريب العمل على ارتفاع.']),
},
'ru':{
 'k01':('Что такое автовышка?',['Автовышка — это кран-манипулятор на грузовике с люлькой для человека.','Тот же кран, что снимает бойлер, поднимает монтажника вывески на четвёртый этаж.','Высоту и вылет меряем от тротуара, а не от стены, и добавляем три-четыре метра запаса.','Проверяем провода, место для опор и грунт, который не просядет.','Полный гид — на сайте tal83.com.']),
 'k02':('Тонна-метр: почему дальше — меньше?',['Кран-манипулятор измеряют в тонна-метрах: вес, умноженный на вылет.','Кран на двенадцать тонна-метров теоретически поднимет четыре тонны на трёх метрах.','А на двенадцати метрах? Всего около тонны.','А на практике ещё меньше: стрела тоже весит.','Решает только грузовая таблица производителя.']),
 'k03':('Что такое гусёк (джиб)?',['Джиб — это дополнительная стрела на конце основной.','Он добавляет высоту и вылет, позволяет достать через стену и вокруг препятствий.','Цена: на конце джиба поднимаем меньше.','И вес самого джиба тоже входит в нагрузку.','С джибом или без? Зависит от работы — спросите заранее.']),
 'k04':('Угол стрелы — секрет крановщика',['Поднятая стрела приближает груз — поднимаем больше.','Опущенная стрела отдаляет груз — поднимаем меньше.','Вылет равен длине стрелы, умноженной на косинус угла.','Указатель угла на стреле показывает оператору, где он.','Если угла нет в таблице — берём ближайший меньший.']),
 'k05':('Кран на 100 тонн поднимает 100 тонн?',['Не совсем.','Число в названии крана — это грузоподъёмность на минимальном вылете, с выдвинутыми опорами.','Чем дальше груз, тем сильнее падает грузоподъёмность.','Преимущество большого крана — вылет и высота.','Поэтому для каждого серьёзного подъёма: таблица производителя и план подъёма.']),
 'k06':('Подъёмники — какой вам нужен?',['Ножничный подъёмник идёт строго вверх, с широкой площадкой.','Коленчатый подъёмник достаёт над препятствиями и вокруг них.','Телескопический — для высоты и вылета на открытой площадке.','На подъёмнике управляет тот, кто наверху. На автовышке — оператор снизу.','И всегда: действующий акт проверки и допуск к работе на высоте.']),
},
'en':{
 'k01':('What is a basket crane?',['A basket crane is a knuckle boom crane on a truck, with a person basket at the tip.','The same crane that lowers a water heater also lifts a sign installer to the fourth floor.','Measure height and distance from the sidewalk, not the wall, and add three to four meters of margin.','Check power lines, room for the outriggers, and ground that will not sink.','The full guide is on tal83.com.']),
 'k02':('Tonne-metre: why farther means less',['A knuckle boom crane is rated in tonne-metres: weight times distance.','A twelve tonne-metre crane can, in theory, lift four tonnes at three metres.','But at twelve metres? Only about one tonne.','In practice even less, because the boom itself has weight.','Only the manufacturer load chart decides.']),
 'k03':('What is a jib on a crane?',['A jib is an extra arm attached to the tip of the main boom.','It adds height and reach, getting over walls and around obstacles.','The price: you lift less at the jib tip.','And the jib weight itself counts as part of the load.','With or without a jib? It depends on the job. Ask first.']),
 'k04':('Boom angle – the operator secret',['A steep boom brings the load closer, so you lift more.','A flat boom pushes the load out, so you lift less.','Horizontal reach is boom length times the cosine of the angle.','The angle indicator on the boom tells the operator where he stands.','If the angle is not in the chart, use the next lower one.']),
 'k05':('Does a 100-tonne crane lift 100 tonnes?',['Not exactly.','The number in the name is the capacity at the shortest radius, with outriggers fully out.','The farther the load, the more the capacity drops.','A big crane wins on distance and height.','So every big lift needs the manufacturer chart and a lift plan.']),
 'k06':('Lifting platforms – which one fits?',['A scissor lift goes straight up, with a wide deck.','An articulating boom reaches up and over obstacles.','A telescopic boom gives height and reach in open spaces.','On a platform, the person on top controls it. On a basket crane, the operator works from the ground.','Either way: a valid inspection and work-at-height training.']),
},
'fr':{
 'k01':("Qu'est-ce qu'une grue à nacelle ?",["Une grue à nacelle, c'est une grue articulée sur camion, avec une nacelle pour une personne.","La même grue qui descend un chauffe-eau monte aussi le poseur d'enseigne au quatrième étage.","On mesure la hauteur et la distance depuis le trottoir, pas depuis le mur, et on ajoute trois à quatre mètres de marge.","On vérifie les lignes électriques, la place pour les stabilisateurs et un sol qui ne s'enfonce pas.","Le guide complet est sur tal83.com."]),
 'k02':('Tonne-mètre : pourquoi plus loin, c\'est moins',["Une grue articulée se mesure en tonnes-mètres : le poids multiplié par la distance.","Une grue de douze tonnes-mètres lève en théorie quatre tonnes à trois mètres.","Mais à douze mètres ? Environ une tonne seulement.","En pratique encore moins, car la flèche elle-même pèse.","Seul l'abaque de charge du fabricant fait foi."]),
 'k03':("C'est quoi un jib sur une grue ?",["Le jib est un bras supplémentaire fixé au bout de la flèche principale.","Il ajoute de la hauteur et de la portée, et passe au-dessus des murs et autour des obstacles.","Le prix : au bout du jib, on lève moins.","Et le poids du jib compte dans la charge.","Avec ou sans jib ? Ça dépend du chantier. Demandez avant."]),
 'k04':("L'angle de flèche, le secret du grutier",["Une flèche relevée rapproche la charge : on lève plus.","Une flèche basse éloigne la charge : on lève moins.","La portée est la longueur de flèche multipliée par le cosinus de l'angle.","L'indicateur d'angle sur la flèche dit au grutier où il en est.","Si l'angle n'est pas dans l'abaque, on prend le suivant plus bas."]),
 'k05':('Une grue de 100 tonnes lève 100 tonnes ?',["Pas vraiment.","Le chiffre dans le nom, c'est la capacité au rayon le plus court, stabilisateurs sortis.","Plus la charge s'éloigne, plus la capacité baisse.","L'atout d'une grosse grue, c'est la portée et la hauteur.","Pour chaque gros levage : abaque du fabricant et plan de levage."]),
 'k06':('Nacelles élévatrices : laquelle choisir ?',["La nacelle ciseaux monte tout droit, avec une grande plateforme.","La nacelle articulée passe au-dessus et autour des obstacles.","La nacelle télescopique donne hauteur et portée en terrain dégagé.","Sur une nacelle, c'est la personne en haut qui pilote. Sur une grue à nacelle, le grutier est en bas.","Dans tous les cas : contrôle à jour et formation au travail en hauteur."]),
},
}
n=0
for lang,d in T.items():
    for k,(title,lines) in d.items():
        jid=k if lang=='he' else '%s-%s'%(lang,k)
        job={'id':jid,'title':title,'lines':lines,'photos':PH[k],'lang':lang,'voice':V[lang],'rate':'+4%','presenter':True}
        json.dump(job,open('jobs/%s.json'%jid,'w',encoding='utf-8'),ensure_ascii=False,indent=1); n+=1
print(n)
