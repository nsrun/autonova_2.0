import re
import datetime
from django import forms
from django.core.exceptions import ValidationError
from .models import VehicleListing, SparePartListing, Category

CURRENT_YEAR = datetime.datetime.now().year

KNOWN_VEHICLE_BRANDS = {
    'maruti','suzuki','hyundai','tata','honda','toyota','mahindra','kia',
    'volkswagen','vw','skoda','renault','nissan','mg','jeep','ford','fiat',
    'chevrolet','citroen','datsun','isuzu','bmw','mercedes','mercedes-benz',
    'audi','volvo','land rover','jaguar','lexus','porsche','bentley',
    'rolls royce','ferrari','lamborghini',
    'bajaj','hero','royal enfield','yamaha','kawasaki','ktm','triumph',
    'harley davidson','harley','jawa','cfmoto','benelli','tvs','ola','ather',
    'revolt','ashok leyland','eicher','force',
    'john deere','swaraj','sonalika','new holland','kubota','powertrac',
    'captain','massey ferguson',
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

PART_TYPE_VALID_PARTS = {
    'engine':       ['piston','crankshaft','camshaft','cylinder','valve','gasket',
                     'timing','oil pump','water pump','fuel pump','turbo','injector',
                     'carburetor','connecting rod','engine','motor','rocker','intercooler'],
    'body':         ['bumper','bonnet','hood','fender','door','mirror','windshield',
                     'windscreen','glass','grille','spoiler','roof','panel','mudguard',
                     'boot','quarter panel','sill','body kit','side mirror'],
    'electrical':   ['alternator','starter','ecu','sensor','wiring','harness','coil',
                     'spark plug','glow plug','switch','relay','fuse','horn',
                     'speedometer','instrument','cluster','blower','fan','module'],
    'suspension':   ['shock','strut','control arm','tie rod','ball joint','bearing',
                     'stabilizer','spring','bushing','wishbone','knuckle','trailing'],
    'brakes':       ['brake pad','brake disc','brake drum','caliper','master cylinder',
                     'brake booster','brake shoe','brake kit','abs','brake hose'],
    'transmission': ['gearbox','clutch','flywheel','differential','driveshaft',
                     'cv joint','propeller shaft','gear','axle','torque','half shaft'],
    'exhaust':      ['muffler','silencer','exhaust','catalytic','dpf','egr',
                     'manifold','downpipe','resonator'],
    'tyres':        ['tyre','tire','tube','rim','wheel','alloy','tpms'],
    'interior':     ['seat','dashboard','steering wheel','airbag','carpet','mat',
                     'door panel','headliner','sun visor','rear view mirror',
                     'gear knob','console','armrest','upholstery'],
    'lights':       ['headlight','tail light','taillight','fog light','drl',
                     'indicator','bulb','led','projector','lamp','turn signal'],
    'battery':      ['battery','ev battery','cell','module','terminal'],
    'filters':      ['filter','strainer'],
    'other':        [],
}


def _fuzzy_brand_check(brand_input, brand_set):
    bl = brand_input.lower().strip()
    if not bl:
        return True, None
    if bl in brand_set:
        return True, None
    for b in brand_set:
        if bl in b or b in bl:
            return True, None
    corrections = {
        'mercedez':'Mercedes','mercides':'Mercedes','hunday':'Hyundai',
        'hyndai':'Hyundai','toyata':'Toyota','maruthi':'Maruti',
        'kawasaky':'Kawasaki','yamha':'Yamaha','yammaha':'Yamaha',
        'bossch':'Bosch','bosche':'Bosch','brembro':'Brembo',
    }
    if bl in corrections:
        return False, corrections[bl]
    return False, None


class VehicleListingForm(forms.ModelForm):
    class Meta:
        model  = VehicleListing
        fields = [
            'title','category','brand','model','variant','year',
            'condition','fuel_type','transmission','km_driven','engine_cc',
            'num_owners','color','rto_state','registration_year',
            'insurance','insurance_valid_until','price','is_negotiable',
            'location','description',
        ]
        widgets = {
            'title':                forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. 2020 Honda City V MT Petrol — Single Owner'}),
            'category':             forms.Select(attrs={'class':'form-select'}),
            'brand':                forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Maruti, Honda, Royal Enfield'}),
            'model':                forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Swift, Activa, Bullet 350'}),
            'variant':              forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. VXi, ZXi+ (optional)'}),
            'year':                 forms.NumberInput(attrs={'class':'form-control','placeholder':'e.g. 2019','min':1980,'max':CURRENT_YEAR}),
            'condition':            forms.Select(attrs={'class':'form-select'}),
            'fuel_type':            forms.Select(attrs={'class':'form-select'}),
            'transmission':         forms.Select(attrs={'class':'form-select'}),
            'km_driven':            forms.NumberInput(attrs={'class':'form-control','placeholder':'e.g. 45000','min':0}),
            'engine_cc':            forms.NumberInput(attrs={'class':'form-control','placeholder':'e.g. 1197','min':0}),
            'num_owners':           forms.Select(attrs={'class':'form-select'}),
            'color':                forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Pearl White'}),
            'rto_state':            forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. MH, TN, KA'}),
            'registration_year':    forms.NumberInput(attrs={'class':'form-control','placeholder':'e.g. 2020','min':1980,'max':CURRENT_YEAR}),
            'insurance':            forms.Select(attrs={'class':'form-select'}),
            'insurance_valid_until':forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'price':                forms.NumberInput(attrs={'class':'form-control','placeholder':'0','step':'1000','min':0}),
            'is_negotiable':        forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'location':             forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Mumbai, Maharashtra'}),
            'description':          forms.Textarea(attrs={'class':'form-control','rows':5,'placeholder':'Describe the vehicle — service history, modifications, reason for selling...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['category'].queryset = Category.objects.filter(category_type='vehicle')
        except Exception:
            pass

    def clean_title(self):
        title = self.cleaned_data.get('title','').strip()
        if len(title) < 10:
            raise ValidationError("Title is too short. Include year, brand, model and variant.")
        if len(title) > 200:
            raise ValidationError("Title is too long. Keep it under 200 characters.")
        if re.fullmatch(r'[\d\s]+', title):
            raise ValidationError("Title cannot be only numbers.")
        return title

    def clean_brand(self):
        brand = self.cleaned_data.get('brand','').strip()
        if not brand:
            raise ValidationError("Brand is required.")
        if len(brand) < 2:
            raise ValidationError("Brand name is too short.")
        is_valid, suggestion = _fuzzy_brand_check(brand, KNOWN_VEHICLE_BRANDS)
        if not is_valid:
            msg = f"'{brand}' is not a recognised vehicle brand."
            if suggestion:
                msg += f" Did you mean '{suggestion}'?"
            else:
                msg += " Please enter the correct manufacturer name (e.g. Maruti, Honda, Toyota)."
            raise ValidationError(msg)
        return brand.title()

    def clean_model(self):
        model = self.cleaned_data.get('model','').strip()
        if not model:
            raise ValidationError("Model name is required.")
        if len(model) < 2:
            raise ValidationError("Model name is too short.")
        if re.fullmatch(r'[\d\s]+', model):
            raise ValidationError("Model name cannot be only numbers.")
        return model

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year is None:
            raise ValidationError("Year is required.")
        if year < 1980:
            raise ValidationError("Year cannot be before 1980.")
        if year > CURRENT_YEAR:
            raise ValidationError(f"Year cannot be in the future. Maximum is {CURRENT_YEAR}.")
        return year

    def clean_km_driven(self):
        km = self.cleaned_data.get('km_driven')
        if km is None:
            raise ValidationError("KM driven is required.")
        if km < 0:
            raise ValidationError("KM driven cannot be negative.")
        if km > 2000000:
            raise ValidationError("KM driven value seems unrealistic. Please check.")
        return km

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise ValidationError("Price is required.")
        if price <= 0:
            raise ValidationError("Price must be greater than ₹0.")
        if price < 5000:
            raise ValidationError("Minimum listing price is ₹5,000.")
        if price > 100000000:
            raise ValidationError("Price seems too high. Maximum is ₹10 Crore.")
        return price

    def clean_engine_cc(self):
        cc = self.cleaned_data.get('engine_cc')
        if cc is not None and cc > 20000:
            raise ValidationError("Engine CC seems too high. Please check.")
        return cc

    def clean_location(self):
        loc = self.cleaned_data.get('location','').strip()
        if not loc:
            raise ValidationError("Location is required.")
        if len(loc) < 3:
            raise ValidationError("Please enter a valid city or location.")
        if re.fullmatch(r'[\d\s]+', loc):
            raise ValidationError("Location cannot be only numbers.")
        return loc

    def clean_description(self):
        desc = self.cleaned_data.get('description','').strip()
        if not desc:
            raise ValidationError("Description is required.")
        if len(desc) < 20:
            raise ValidationError("Description is too short. Please add at least 20 characters.")
        return desc

    def clean_rto_state(self):
        rto = self.cleaned_data.get('rto_state','').strip()
        if rto and rto.isdigit():
            raise ValidationError("RTO state should be a state code like MH, TN, KA.")
        return rto.upper() if rto else rto

    def clean_registration_year(self):
        reg_year = self.cleaned_data.get('registration_year')
        year     = self.cleaned_data.get('year')
        if reg_year:
            if reg_year < 1980:
                raise ValidationError("Registration year cannot be before 1980.")
            if reg_year > CURRENT_YEAR:
                raise ValidationError("Registration year cannot be in the future.")
            if year and reg_year < year:
                raise ValidationError("Registration year cannot be before the manufacture year.")
        return reg_year

    def clean(self):
        cleaned   = super().clean()
        condition = cleaned.get('condition')
        km        = cleaned.get('km_driven', 0) or 0
        year      = cleaned.get('year')

        if condition == 'new' and km and km > 500:
            self.add_error('km_driven',
                "A 'Brand New' vehicle should have 0 km. "
                "Please select the correct condition or fix the KM value.")

        if year and condition:
            age = CURRENT_YEAR - year
            if age > 15 and condition == 'like_new':
                self.add_error('condition',
                    f"A {year} vehicle ({age} years old) cannot be 'Like New'. "
                    "Please select Good, Fair, or Poor condition.")
            if age == 0 and condition == 'poor':
                self.add_error('condition', "A brand new vehicle cannot be in 'Poor' condition.")

        insurance      = cleaned.get('insurance')
        insurance_date = cleaned.get('insurance_valid_until')
        if insurance == 'comprehensive' and not insurance_date:
            self.add_error('insurance_valid_until',
                "Please enter the insurance expiry date for Comprehensive insurance.")
        return cleaned


class SparePartForm(forms.ModelForm):
    class Meta:
        model  = SparePartListing
        fields = [
            'title','category','part_name','part_number','part_type',
            'condition','brand','description',
            'compatible_vehicle_type','compatible_brand','compatible_model',
            'compatible_year_from','compatible_year_to',
            'quantity','price','is_negotiable','location',
        ]
        widgets = {
            'title':                  forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Maruti Swift Front Brake Pad Set (2015–2022) — Bosch'}),
            'category':               forms.Select(attrs={'class':'form-select'}),
            'part_name':              forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Brake Pad, Alternator, Headlight Assembly'}),
            'part_number':            forms.TextInput(attrs={'class':'form-control','placeholder':'OEM part number (optional)'}),
            'part_type':              forms.Select(attrs={'class':'form-select'}),
            'condition':              forms.Select(attrs={'class':'form-select'}),
            'brand':                  forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Bosch, Minda, MRF (optional)'}),
            'description':            forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'Describe the part — why removed, usage, any defects...'}),
            'compatible_vehicle_type':forms.Select(attrs={'class':'form-select'}),
            'compatible_brand':       forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Maruti, Honda'}),
            'compatible_model':       forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Swift, City, WagonR'}),
            'compatible_year_from':   forms.NumberInput(attrs={'class':'form-control','placeholder':'From year','min':1980,'max':CURRENT_YEAR}),
            'compatible_year_to':     forms.NumberInput(attrs={'class':'form-control','placeholder':'To year','min':1980,'max':CURRENT_YEAR}),
            'quantity':               forms.NumberInput(attrs={'class':'form-control','min':1}),
            'price':                  forms.NumberInput(attrs={'class':'form-control','placeholder':'0','step':'10','min':0}),
            'is_negotiable':          forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'location':               forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Delhi, Mumbai'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['category'].queryset = Category.objects.filter(category_type='sparepart')
        except Exception:
            pass

    def clean_title(self):
        title = self.cleaned_data.get('title','').strip()
        if len(title) < 8:
            raise ValidationError("Title is too short. Include brand, part name and compatibility.")
        if len(title) > 200:
            raise ValidationError("Title is too long.")
        return title

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
        is_valid, suggestion = _fuzzy_brand_check(brand, KNOWN_PART_BRANDS)
        if not is_valid:
            msg = f"'{brand}' is not a recognised part brand."
            if suggestion:
                msg += f" Did you mean '{suggestion}'?"
            else:
                msg += " Enter a known brand (e.g. Bosch, MRF, Minda) or leave blank."
            raise ValidationError(msg)
        return brand.title()

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise ValidationError("Price is required.")
        if price <= 0:
            raise ValidationError("Price must be greater than ₹0.")
        if price < 10:
            raise ValidationError("Minimum price is ₹10.")
        if price > 10000000:
            raise ValidationError("Price too high. Maximum is ₹1 Crore.")
        return price

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty < 1:
            raise ValidationError("Quantity must be at least 1.")
        if qty > 10000:
            raise ValidationError("Quantity cannot exceed 10,000.")
        return qty

    def clean_location(self):
        loc = self.cleaned_data.get('location','').strip()
        if not loc:
            raise ValidationError("Location is required.")
        if len(loc) < 3:
            raise ValidationError("Please enter a valid city or location.")
        return loc

    def clean_description(self):
        desc = self.cleaned_data.get('description','').strip()
        if not desc:
            raise ValidationError("Description is required.")
        if len(desc) < 15:
            raise ValidationError("Description is too short. Add at least 15 characters.")
        return desc

    def clean_compatible_year_from(self):
        y = self.cleaned_data.get('compatible_year_from')
        if y and (y < 1980 or y > CURRENT_YEAR):
            raise ValidationError(f"Year must be between 1980 and {CURRENT_YEAR}.")
        return y

    def clean_compatible_year_to(self):
        y = self.cleaned_data.get('compatible_year_to')
        if y and (y < 1980 or y > CURRENT_YEAR):
            raise ValidationError(f"Year must be between 1980 and {CURRENT_YEAR}.")
        return y

    def clean(self):
        cleaned   = super().clean()
        part_type = cleaned.get('part_type','')
        part_name = (cleaned.get('part_name') or '').lower()
        yr_from   = cleaned.get('compatible_year_from')
        yr_to     = cleaned.get('compatible_year_to')
        compat_b  = (cleaned.get('compatible_brand') or '').lower()

        if part_type and part_type != 'other' and part_name:
            valid_kws = PART_TYPE_VALID_PARTS.get(part_type, [])
            if valid_kws and not any(kw in part_name for kw in valid_kws):
                correct_type = None
                correct_label = None
                for ptype, kws in PART_TYPE_VALID_PARTS.items():
                    if ptype == 'other': continue
                    if any(kw in part_name for kw in kws):
                        correct_type  = ptype
                        correct_label = dict(SparePartListing.PART_TYPE_CHOICES).get(ptype, ptype)
                        break
                selected_label = dict(SparePartListing.PART_TYPE_CHOICES).get(part_type, part_type)
                if correct_label:
                    self.add_error('part_type',
                        f"'{cleaned.get('part_name')}' is not a {selected_label} part. "
                        f"It belongs to '{correct_label}'. Please select the correct Part Type.")
                else:
                    self.add_error('part_type',
                        f"'{cleaned.get('part_name')}' does not match '{selected_label}'. "
                        f"Please verify or use 'Other'.")

        if yr_from and yr_to and yr_from > yr_to:
            self.add_error('compatible_year_to', "'Year To' must be after 'Year From'.")

        if compat_b:
            all_parts = set()
            for kws in PART_TYPE_VALID_PARTS.values():
                all_parts.update(kws)
            if any(p in compat_b for p in all_parts):
                self.add_error('compatible_brand',
                    "This field should be a vehicle brand/model (e.g. 'Maruti Swift'), not a part name.")
        return cleaned


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Search vehicles, parts, brands...'})
    )
    listing_type = forms.ChoiceField(
        required=False,
        choices=[('','All Listings'),('vehicle','Vehicles'),('sparepart','Spare Parts')],
        widget=forms.Select(attrs={'class':'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=None, required=False, empty_label='All Categories',
        widget=forms.Select(attrs={'class':'form-select'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Min ₹','min':0})
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Max ₹','min':0})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'City / State'})
    )
    fuel_type = forms.ChoiceField(
        required=False,
        choices=[('','Any Fuel'),('petrol','Petrol'),('diesel','Diesel'),
                 ('cng','CNG'),('electric','Electric'),('hybrid','Hybrid')],
        widget=forms.Select(attrs={'class':'form-select'})
    )
    max_km = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Max KM driven','min':0})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['category'].queryset = Category.objects.all()
        except Exception:
            pass

    def clean(self):
        cleaned   = super().clean()
        min_price = cleaned.get('min_price')
        max_price = cleaned.get('max_price')
        if min_price and max_price and min_price > max_price:
            self.add_error('max_price', "Max price must be greater than min price.")
        return cleaned