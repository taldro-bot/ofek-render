"""28.11 Tal: BLOW MIND crane promo (Tel Aviv at height): FPV crane-up → zoom-punch → carabiner snap macro (clink + sub-bass)
→ aerial pull-back over Tel Aviv. Same engine as hanukkah_blow (speed-ramp, sound design, no music). python crane_blow.py LANG out.mp4"""
import sys, os
import hanukkah_blow as B
B.DIR = os.path.join(B.ROOT, 'media', 'promo', 'tlv')
B.FIRE = False
B.END = {
 'he': ('בטיחות בכל מחיר. בלי פשרות.', 'אופק את טל מנופים', 'מנוף סל · עבודה בגובה · הדרכות · 050-9081114'),
 'en': ('Safety at any cost. No compromise.', 'Ofek et Tal Cranes', 'Basket crane · Work at height · +972-50-908-1114'),
 'ru': ('Безопасность любой ценой. Без компромиссов.', 'Ofek et Tal Cranes', 'Автовышка · Работы на высоте · +972-50-908-1114'),
 'fr': ('La sécurité à tout prix. Sans compromis.', 'Ofek et Tal Cranes', 'Nacelle · Travail en hauteur · +972-50-908-1114'),
}
if __name__ == '__main__':
    B.main()
