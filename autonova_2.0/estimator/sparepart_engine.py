"""
AutoNova — Spare Part Estimation Engine v2.0
Validates inputs strictly, then uses Claude AI (with heuristic fallback).
"""
import os, json, logging, difflib
from decimal import Decimal

logger = logging.getLogger(__name__)

try:
    import anthropic
    _SDK_OK = True
except ImportError:
    _SDK_OK = False

PART_TYPE_KEYWORDS = {
    'engine':       ['piston','crankshaft','camshaft','cylinder','valve','gasket',
                     'timing','oil pump','water pump','fuel pump','turbo','injector',
                     'carburetor','engine','motor','connecting rod','intercooler'],
    'body':         ['bumper','bonnet','hood','fender','door','mirror','windshield',
                     'windscreen','glass','grille','spoiler','roof','panel','mudguard',
                     'side mirror','boot','sill'],
    'electrical':   ['alternator','starter','ecu','sensor','wiring','harness','coil',
                     'spark plug','glow plug','switch','relay','fuse','horn',
                     'speedometer','instrument','cluster','blower','module'],
    'suspension':   ['shock','strut','control arm','tie rod','ball joint','bearing',
                     'stabilizer','spring','bushing','wishbone','knuckle'],
    'brakes':       ['brake pad','brake disc','brake drum','caliper','master cylinder',
                     'brake booster','brake shoe','brake kit','abs','brake hose'],
    'transmission': ['gearbox','clutch','flywheel','differential','driveshaft',
                     'cv joint','propeller shaft','gear','axle','half shaft'],
    'exhaust':      ['muffler','silencer','exhaust','catalytic','dpf','egr',
                     'manifold','downpipe','resonator'],
    'tyres':        ['tyre','tire','tube','rim','wheel','alloy','tpms'],
    'interior':     ['seat','dashboard','steering wheel','airbag','carpet','mat',
                     'door panel','headliner','sun visor','rear view mirror',
                     'gear knob','console','armrest'],
    'lights':       ['headlight','tail light','taillight','fog light','drl',
                     'indicator','bulb','led','projector','lamp','turn signal'],
    'battery':      ['battery','ev battery','cell','module','terminal'],
    'filters':      ['filter','strainer'],
    'other':        [],
}

PART_TYPE_LABELS = {
    'engine':'Engine Parts','body':'Body Parts','electrical':'Electrical & Electronics',
    'suspension':'Suspension & Steering','brakes':'Brakes',
    'transmission':'Transmission & Gearbox','exhaust':'Exhaust System',
    'tyres':'Tyres & Wheels','interior':'Interior & Accessories',
    'lights':'Lights & Indicators','battery':'Battery & Charging',
    'filters':'Filters & Fluids','other':'Other',
}

KNOWN_BRANDS = {
    'bosch','denso','continental','brembo','bilstein','sachs','valeo','mahle',
    'ntn','nsk','trw','monroe','gabriel','delphi','gates','dayco','moog',
    'minda','lumax','fiem','sona','rane','endurance','motherson','exide',
    'amaron','luminous','mrf','apollo','ceat','jk','bridgestone','michelin',
    'goodyear','yokohama','pirelli','dunlop','ngk','hella','osram','philips',
    'maruti','hyundai','tata','honda','toyota','mahindra','kia','volkswagen',
    'skoda','renault','nissan','bmw','mercedes','audi','volvo',
    'bajaj','hero','royal enfield','yamaha','kawasaki','ktm','tvs',
    'oem','genuine','original','aftermarket','generic','local','unbranded',
}

BRAND_CORRECTIONS = {
    'mercedez':'mercedes','mercides':'mercedes','hunday':'hyundai',
    'hyndai':'hyundai','toyata':'toyota','maruthi':'maruti',
    'bossch':'bosch','bosche':'bosch','densso':'denso','brembro':'brembo',
    'mosnroe':'monroe','kawasaky':'kawasaki','yamha':'yamaha',
}

class ValidationError(Exception):
    pass

def _validate(part_type, part_name, brand, condition,
               compatible_vehicle_type, compatible_brand, quantity):
    warnings = []

    if not part_type:
        raise ValidationError("Please select a Part Type.")
    if not part_name or not part_name.strip():
        raise ValidationError("Part Name is required.")
    if not condition:
        raise ValidationError("Please select the Part Condition.")
    if not compatible_vehicle_type:
        raise ValidationError("Please select the Compatible Vehicle Type.")

    pn = part_name.lower().strip()
    pt = part_type.lower().strip()

    if len(pn) < 3:
        raise ValidationError("Part Name is too short. Enter the full part name.")
    if not any(c.isalpha() for c in pn):
        raise ValidationError("Part Name must contain letters.")

    if pt != 'other':
        valid_kws = PART_TYPE_KEYWORDS.get(pt, [])
        if valid_kws and not any(kw in pn for kw in valid_kws):
            correct_type = None
            for ptype, kws in PART_TYPE_KEYWORDS.items():
                if ptype == 'other': continue
                if any(kw in pn for kw in kws):
                    correct_type = ptype; break
            selected_label = PART_TYPE_LABELS.get(pt, pt.title())
            if correct_type:
                correct_label = PART_TYPE_LABELS.get(correct_type, correct_type.title())
                raise ValidationError(
                    f'"{part_name}" is not a {selected_label} part. '
                    f'It belongs to "{correct_label}". '
                    f'Please change Part Type to "{correct_label}".')
            else:
                warnings.append({'message': f'"{part_name}" doesn\'t match known {selected_label} parts.',
                                  'suggestion': 'If correct, select "Other" as Part Type.'})

    corrected_brand = brand
    if brand and brand.strip():
        bl = brand.lower().strip()
        if bl not in KNOWN_BRANDS:
            if bl in BRAND_CORRECTIONS:
                corrected_brand = BRAND_CORRECTIONS[bl].title()
                warnings.append({'message': f'"{brand}" looks like a misspelling.',
                                  'suggestion': f'Did you mean "{corrected_brand}"? Using corrected brand.'})
            else:
                close = difflib.get_close_matches(bl, KNOWN_BRANDS, n=1, cutoff=0.75)
                if close:
                    corrected_brand = close[0].title()
                    warnings.append({'message': f'"{brand}" is not a recognised brand.',
                                      'suggestion': f'Did you mean "{corrected_brand}"?'})
                else:
                    partial = [b for b in KNOWN_BRANDS if bl in b or b in bl]
                    if not partial:
                        warnings.append({'message': f'"{brand}" is not a recognised automotive brand.',
                                          'suggestion': 'Price estimated as Generic. Leave blank for generic pricing.'})

    try:
        qty = int(quantity or 1)
        if qty < 1:   raise ValidationError("Quantity must be at least 1.")
        if qty > 1000: raise ValidationError("Quantity cannot exceed 1,000.")
    except (TypeError, ValueError):
        raise ValidationError("Quantity must be a whole number.")

    if compatible_brand:
        cb = compatible_brand.lower()
        all_parts = set()
        for kws in PART_TYPE_KEYWORDS.values():
            all_parts.update(kws)
        if any(p in cb for p in all_parts):
            warnings.append({'message': f'"{compatible_brand}" looks like a part name, not a vehicle brand.',
                              'suggestion': 'This field should be a vehicle brand/model like "Maruti Swift".'})

    return {
        'part_type': pt, 'part_name': part_name.strip(),
        'brand': (corrected_brand or '').strip(), 'condition': condition,
        'compatible_vehicle_type': compatible_vehicle_type,
        'compatible_brand': (compatible_brand or '').strip(), 'quantity': qty,
    }, warnings

_PROMPT = """\
You are an expert Indian automotive spare parts market analyst. It is 2025.
Estimate the fair market price of this spare part in India (INR).

Part Details:
  Category            : {part_type}
  Part Name           : {part_name}
  Brand / Manufacturer: {brand}
  Condition           : {condition}
  Compatible Vehicle  : {compatible_vehicle_type}
  Compatible Brand    : {compatible_brand}
  Quantity            : {quantity}

Consider: 2024-25 Indian market prices, brand tier (Bosch/Denso = 60-90% premium; Minda/MRF = 10-30%;
generic = baseline), condition multipliers (New=100%, OEM=85%, Refurbished=60%, Used Good=45%, Used Fair=27%),
vehicle type (truck=2-3x car; bike=40-55%), compatible brand premium (luxury=60-120% extra),
bulk discount for qty>2.

Return ONLY valid JSON:
{{
  "estimated_price": <integer nearest 50, TOTAL for quantity>,
  "low_price": <integer nearest 50, ~15% below>,
  "high_price": <integer nearest 50, ~20% above>,
  "unit_price": <integer, single unit price>,
  "confidence": <"High"|"Medium"|"Low">,
  "explanation": <2-3 sentences: brand tier, condition effect, key factor>
}}"""

def _get_api_key():
    key = os.environ.get('ANTHROPIC_API_KEY')
    if key: return key
    try:
        from django.conf import settings
        return getattr(settings, 'ANTHROPIC_API_KEY', None)
    except Exception:
        return None

def _call_claude(prompt):
    client = anthropic.Anthropic(api_key=_get_api_key())
    msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=400,
        messages=[{"role":"user","content":prompt}]
    )
    raw = msg.content[0].text.strip()
    if raw.startswith('```'):
        parts = raw.split('```')
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith('json'): raw = raw[4:]
    return json.loads(raw.strip())

_BASE  = {'engine':6000,'body':10000,'electrical':4000,'suspension':4000,
          'brakes':2500,'transmission':15000,'exhaust':5000,'tyres':5500,
          'interior':6000,'lights':4000,'battery':6500,'filters':700,'other':3500}
_CF    = {'new':1.00,'oem':0.87,'used_good':0.47,'used_fair':0.27,'refurbished':0.60}
_VTF   = {'car':1.0,'bike':0.50,'truck':2.4,'tractor':2.0,'universal':0.85}
_BF    = {'bosch':1.72,'denso':1.65,'brembo':1.90,'trw':1.60,'monroe':1.55,
          'mrf':1.30,'amaron':1.25,'exide':1.20,'apollo':1.20,'minda':1.15,
          'bridgestone':1.40,'michelin':1.50,'generic':0.70,'local':0.55}

def _heuristic(cleaned):
    pt  = cleaned['part_type']; cond = cleaned['condition']
    bl  = cleaned['brand'].lower(); vt = cleaned['compatible_vehicle_type'].lower()
    qty = cleaned['quantity']
    unit = float(_BASE.get(pt,3500)) * _CF.get(cond,0.47) * _VTF.get(vt,1.0) * _BF.get(bl,1.00)
    if qty > 1:
        bulk = 0.92 if qty<=5 else (0.87 if qty<=10 else 0.82)
        total = unit * qty * bulk
    else:
        total = unit
    total = max(50, round(total/50)*50)
    return {
        'estimated_price': Decimal(str(int(total))),
        'low_price':       Decimal(str(max(50, round(total*0.83/50)*50))),
        'high_price':      Decimal(str(round(total*1.22/50)*50)),
        'unit_price':      Decimal(str(max(50, round(unit/50)*50))),
        'explanation':     f"Heuristic estimate for {cleaned['part_name']} ({cleaned['brand'] or 'Generic'}). AI unavailable.",
        'confidence':      'Medium',
    }

def estimate_spare_part_price(part_type, part_name, brand, condition,
                               compatible_vehicle_type='car',
                               compatible_brand='', quantity=1):
    try:
        cleaned, warnings = _validate(part_type, part_name, brand, condition,
                                       compatible_vehicle_type, compatible_brand, quantity)
    except ValidationError as e:
        return {'error':str(e),'warnings':[],'estimated_price':None,'low_price':None,
                'high_price':None,'unit_price':None,'explanation':None,'confidence':None}

    result = None
    if _SDK_OK and _get_api_key():
        try:
            prompt = _PROMPT.format(
                part_type=PART_TYPE_LABELS.get(cleaned['part_type'], cleaned['part_type']),
                part_name=cleaned['part_name'],
                brand=cleaned['brand'] or 'Generic/Unbranded',
                condition=cleaned['condition'],
                compatible_vehicle_type=cleaned['compatible_vehicle_type'],
                compatible_brand=cleaned['compatible_brand'] or 'Universal',
                quantity=cleaned['quantity'],
            )
            data = _call_claude(prompt)
            est  = int(data['estimated_price'])
            low  = int(data.get('low_price',0))
            high = int(data.get('high_price',0))
            unit = int(data.get('unit_price', est))
            if est <= 0: raise ValueError("Zero price")
            if low <= 0 or low >= est: low  = round(est*0.83/50)*50
            if high <= est:            high = round(est*1.20/50)*50
            result = {'estimated_price':Decimal(str(max(50,est))),
                      'low_price':Decimal(str(max(50,low))),
                      'high_price':Decimal(str(high)),
                      'unit_price':Decimal(str(max(50,unit))),
                      'explanation':str(data.get('explanation','')),
                      'confidence':str(data.get('confidence','Medium'))}
        except Exception as exc:
            logger.warning("AI spare part engine failed (%s). Using heuristic.", exc)

    if result is None:
        result = _heuristic(cleaned)
    result['warnings'] = warnings
    result['error']    = None
    return result