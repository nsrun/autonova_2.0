import re
import datetime
from django import forms
from django.core.exceptions import ValidationError

CURRENT_YEAR = datetime.datetime.now().year

VEHICLE_TYPE_CHOICES = [
    ('', 'Select Vehicle Type'),
    ('cars',     'Car / SUV'),
    ('bikes',    'Bike / Motorcycle'),
    ('scooters', 'Scooter'),
    ('trucks',   'Truck / Commercial'),
    ('tractors', 'Tractor / Farm'),
]
CONDITION_CHOICES = [
    ('', 'Select Condition'),
    ('new',      'Brand New'),
    ('like_new', 'Like New'),
    ('good',     'Good'),
    ('fair',     'Fair'),
    ('poor',     'Poor / For Parts'),
]
FUEL_TYPE_CHOICES = [
    ('', 'Select Fuel Type'),
    ('petrol',   'Petrol'),
    ('diesel',   'Diesel'),
    ('cng',      'CNG'),
    ('electric', 'Electric'),
    ('hybrid',   'Hybrid'),
    ('lpg',      'LPG'),
]
OWNER_CHOICES = [
    ('', 'Select Owners'),
    ('1', '1st Owner'),
    ('2', '2nd Owner'),
    ('3', '3rd Owner'),
    ('4', '4th Owner or more'),
]
INSURANCE_CHOICES = [
    ('', 'Select Insurance'),
    ('comprehensive', 'Comprehensive'),
    ('third_party',   'Third Party'),
    ('expired',       'Expired'),
    ('none',          'None'),
]
PART_TYPE_CHOICES = [
    ('', 'Select Part Type'),
    ('engine',       'Engine Parts'),
    ('body',         'Body Parts'),
    ('electrical',   'Electrical & Electronics'),
    ('suspension',   'Suspension & Steering'),
    ('brakes',       'Brakes'),
    ('transmission', 'Transmission & Gearbox'),
    ('exhaust',      'Exhaust System'),
    ('tyres',        'Tyres & Wheels'),
    ('interior',     'Interior & Accessories'),
    ('lights',       'Lights & Indicators'),
    ('battery',      'Battery & Charging'),
    ('filters',      'Filters & Fluids'),
    ('other',        'Other'),
]
PART_CONDITION_CHOICES = [
    ('', 'Select Condition'),
    ('new',         'Brand New'),
    ('oem',         'OEM / Original (removed from vehicle)'),
    ('used_good',   'Used – Good Condition'),
    ('used_fair',   'Used – Fair Condition'),
    ('refurbished', 'Refurbished / Reconditioned'),
]
COMPAT_VEHICLE_CHOICES = [
    ('', 'Select Vehicle Type'),
    ('car',       'Car'),
    ('bike',      'Bike / Scooter'),
    ('truck',     'Truck / Commercial'),
    ('tractor',   'Tractor / Farm'),
    ('universal', 'Universal / All Vehicles'),
]

KNOWN_VEHICLE_BRANDS = {
    'maruti','suzuki','hyundai','tata','honda','toyota','mahindra','kia',
    'volkswagen','vw','skoda','renault','nissan','mg','jeep','ford','fiat',
    'chevrolet','citroen','bmw','mercedes','mercedes-benz','audi','volvo',
    'land rover','jaguar','lexus','porsche','bentley','rolls royce',
    'bajaj','hero','royal enfield','yamaha','kawasaki','ktm','triumph',
    'harley davidson','harley','jawa','tvs','ola','ather','revolt',
    'ashok leyland','eicher','force','john deere','swaraj','sonalika',
    'new holland','kubota','powertrac','massey ferguson',
}

KNOWN_PART_BRANDS = {
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

PART_TYPE_KEYWORDS = {
    'engine':       ['piston','crankshaft','camshaft','cylinder','valve','gasket',
                     'timing','oil pump','water pump','fuel pump','turbo','injector',
                     'carburetor','engine','motor','connecting rod','intercooler'],
    'body':         ['bumper','bonnet','hood','fender','door','mirror','windshield',
                     'windscreen','glass','grille','spoiler','roof','panel','mudguard',
                     'side mirror'],
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


def _check_brand(brand, brand_set):
    bl = brand.lower().strip()
    if bl in brand_set:
        return None
    for b in brand_set:
        if bl in b or b in bl:
            return None
    corrections = {
        'mercedez':'Mercedes','mercides':'Mercedes','hunday':'Hyundai',
        'hyndai':'Hyundai','toyata':'Toyota','maruthi':'Maruti',
        'kawasaky':'Kawasaki','yamha':'Yamaha','yammaha':'Yamaha',
        'bossch':'Bosch','bosche':'Bosch','brembro':'Brembo',
    }
    if bl in corrections:
        return f"Did you mean '{corrections[bl]}'?"
    return f"'{brand}' is not a recognised brand. Please check the spelling."


# ── VEHICLE ESTIMATOR FORM ────────────────────────────────────────────
class EstimatorForm(forms.Form):
    vehicle_type = forms.ChoiceField(
        choices=VEHICLE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class':'form-select form-select-lg'})
    )
    brand = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg','placeholder':'e.g. Maruti, Honda, Royal Enfield'})
    )
    model = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg','placeholder':'e.g. Swift, City, Classic 350 (improves accuracy)'})
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class':'form-control form-control-lg','placeholder':'e.g. 2019','min':1980,'max':CURRENT_YEAR})
    )
    condition = forms.ChoiceField(
        choices=CONDITION_CHOICES,
        widget=forms.Select(attrs={'class':'form-select form-select-lg'})
    )
    km_driven = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class':'form-control form-control-lg','placeholder':'e.g. 45000','min':0})
    )
    fuel_type = forms.ChoiceField(
        choices=FUEL_TYPE_CHOICES, required=False,
        widget=forms.Select(attrs={'class':'form-select form-select-lg'})
    )
    num_owners = forms.ChoiceField(
        choices=OWNER_CHOICES, required=False,
        widget=forms.Select(attrs={'class':'form-select form-select-lg'})
    )
    insurance = forms.ChoiceField(
        choices=INSURANCE_CHOICES, required=False,
        widget=forms.Select(attrs={'class':'form-select form-select-lg'})
    )

    def clean_vehicle_type(self):
        vt = self.cleaned_data.get('vehicle_type','').strip()
        if not vt:
            raise ValidationError("Please select a vehicle type.")
        return vt

    def clean_brand(self):
        brand = self.cleaned_data.get('brand','').strip()
        if not brand:
            raise ValidationError("Brand is required.")
        if len(brand) < 2:
            raise ValidationError("Brand name is too short.")
        err = _check_brand(brand, KNOWN_VEHICLE_BRANDS)
        if err:
            raise ValidationError(err)
        return brand.title()

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year is None:
            return year
        if year < 1980:
            raise ValidationError("Year cannot be before 1980.")
        if year > CURRENT_YEAR:
            raise ValidationError(f"Year cannot be in the future. Maximum is {CURRENT_YEAR}.")
        return year

    def clean_km_driven(self):
        km = self.cleaned_data.get('km_driven')
        if km is None:
            return km
        if km < 0:
            raise ValidationError("KM driven cannot be negative.")
        if km > 2000000:
            raise ValidationError("KM driven value seems unrealistic.")
        return km

    def clean_condition(self):
        cond = self.cleaned_data.get('condition','').strip()
        if not cond:
            raise ValidationError("Please select the vehicle condition.")
        return cond

    def clean(self):
        cleaned   = super().clean()
        condition = cleaned.get('condition')
        km        = cleaned.get('km_driven', 0) or 0
        year      = cleaned.get('year')

        if condition == 'new' and km > 500:
            self.add_error('km_driven',
                "KM driven is too high for a 'Brand New' vehicle. "
                "Set KM to 0 or select the correct condition.")
        if year:
            age = CURRENT_YEAR - year
            if age > 12 and condition == 'like_new':
                self.add_error('condition',
                    f"A {year} vehicle ({age} years old) cannot be 'Like New'. "
                    "Please select Good, Fair, or Poor.")
            if age == 0 and condition in ('fair','poor'):
                self.add_error('condition',
                    "A brand-new vehicle cannot be in Fair or Poor condition.")
        return cleaned


# ── SPARE PART ESTIMATOR FORM ─────────────────────────────────────────
class SparePartEstimatorForm(forms.Form):
    part_type = forms.ChoiceField(
        choices=PART_TYPE_CHOICES,
        widget=forms.Select(attrs={'class':'form-select form-select-lg'})
    )
    part_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg','placeholder':'e.g. Brake Pad, Alternator, Headlight'})
    )
    brand = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg','placeholder':'e.g. Bosch, Denso, MRF (optional)'})
    )
    condition = forms.ChoiceField(
        choices=PART_CONDITION_CHOICES,
        widget=forms.Select(attrs={'class':'form-select form-select-lg'})
    )
    compatible_vehicle_type = forms.ChoiceField(
        choices=COMPAT_VEHICLE_CHOICES,
        widget=forms.Select(attrs={'class':'form-select form-select-lg'})
    )
    compatible_brand = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg','placeholder':'e.g. Maruti Swift, Honda City (optional)'})
    )
    quantity = forms.IntegerField(
        required=False, initial=1,
        widget=forms.NumberInput(attrs={'class':'form-control form-control-lg','placeholder':'1','min':1,'max':1000})
    )

    def clean_part_type(self):
        pt = self.cleaned_data.get('part_type','').strip()
        if not pt:
            raise ValidationError("Please select a Part Type.")
        return pt

    def clean_part_name(self):
        pn = self.cleaned_data.get('part_name','').strip()
        if not pn:
            raise ValidationError("Part name is required.")
        if len(pn) < 3:
            raise ValidationError("Part name is too short.")
        if not any(c.isalpha() for c in pn):
            raise ValidationError("Part name must contain letters.")
        return pn

    def clean_brand(self):
        brand = self.cleaned_data.get('brand','').strip()
        if not brand:
            return brand
        bl = brand.lower()
        if bl in KNOWN_PART_BRANDS:
            return brand.title()
        for b in KNOWN_PART_BRANDS:
            if bl in b or b in bl:
                return brand.title()
        corrections = {
            'bossch':'Bosch','bosche':'Bosch','densso':'Denso',
            'brembro':'Brembo','mosnroe':'Monroe',
        }
        if bl in corrections:
            raise ValidationError(f"Did you mean '{corrections[bl]}'? Please correct the brand name.")
        raise ValidationError(
            f"'{brand}' is not a recognised part brand. "
            "Enter a known brand (e.g. Bosch, MRF, Minda) or leave blank for generic.")

    def clean_condition(self):
        cond = self.cleaned_data.get('condition','').strip()
        if not cond:
            raise ValidationError("Please select the part condition.")
        return cond

    def clean_compatible_vehicle_type(self):
        vt = self.cleaned_data.get('compatible_vehicle_type','').strip()
        if not vt:
            raise ValidationError("Please select the compatible vehicle type.")
        return vt

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity') or 1
        if qty < 1:
            raise ValidationError("Quantity must be at least 1.")
        if qty > 1000:
            raise ValidationError("Quantity cannot exceed 1,000.")
        return qty

    def clean(self):
        cleaned   = super().clean()
        part_type = cleaned.get('part_type','')
        part_name = (cleaned.get('part_name') or '').lower()
        compat_b  = (cleaned.get('compatible_brand') or '').lower()

        if part_type and part_type != 'other' and part_name:
            valid_kws = PART_TYPE_KEYWORDS.get(part_type, [])
            if valid_kws and not any(kw in part_name for kw in valid_kws):
                correct_label = None
                for ptype, kws in PART_TYPE_KEYWORDS.items():
                    if ptype == 'other': continue
                    if any(kw in part_name for kw in kws):
                        correct_label = dict(PART_TYPE_CHOICES).get(ptype, ptype)
                        break
                selected_label = dict(PART_TYPE_CHOICES).get(part_type, part_type)
                if correct_label:
                    self.add_error('part_type',
                        f"'{cleaned.get('part_name')}' is not a {selected_label} part — "
                        f"it belongs to '{correct_label}'. Please change the Part Type.")
                else:
                    self.add_error('part_type',
                        f"'{cleaned.get('part_name')}' doesn't match '{selected_label}'. "
                        "Please verify or choose 'Other'.")

        if compat_b:
            all_parts = set()
            for kws in PART_TYPE_KEYWORDS.values():
                all_parts.update(kws)
            if any(p in compat_b for p in all_parts):
                self.add_error('compatible_brand',
                    "This should be a vehicle brand/model (e.g. 'Maruti Swift'), not a part name.")
        return cleaned