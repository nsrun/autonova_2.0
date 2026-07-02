"""
AutoNova — AI Vehicle Price Estimation Engine v10.0
Exhaustive India vehicle database: 2000+ models, 120+ brands
Cars · Bikes · Scooters · Trucks · Commercial · Tractors
"""
import os, json, datetime, logging, difflib
from decimal import Decimal

logger = logging.getLogger(__name__)
try:
    import anthropic; _SDK_OK = True
except ImportError:
    _SDK_OK = False

CURRENT_YEAR = datetime.datetime.now().year

BRAND_VEHICLE_TYPES = {
    # ── CARS ─────────────────────────────────────────────────────
    'maruti':{'cars'},'suzuki':{'cars'},'hyundai':{'cars'},
    'tata':{'cars','trucks'},'honda':{'cars','bikes','scooters'},
    'toyota':{'cars','trucks'},'mahindra':{'cars','trucks','tractors'},
    'kia':{'cars'},'volkswagen':{'cars'},'vw':{'cars'},'skoda':{'cars'},
    'renault':{'cars'},'nissan':{'cars'},'mg':{'cars'},'jeep':{'cars'},
    'ford':{'cars','trucks'},'fiat':{'cars'},'chevrolet':{'cars'},
    'citroen':{'cars'},'datsun':{'cars'},'isuzu':{'cars','trucks'},
    'mini':{'cars'},'mitsubishi':{'cars'},'opel':{'cars'},
    'bmw':{'cars'},'mercedes':{'cars'},'mercedes-benz':{'cars'},
    'audi':{'cars'},'volvo':{'cars','trucks'},'land rover':{'cars'},
    'jaguar':{'cars'},'lexus':{'cars'},'porsche':{'cars'},
    'bentley':{'cars'},'rolls royce':{'cars'},'ferrari':{'cars'},
    'lamborghini':{'cars'},'maserati':{'cars'},'aston martin':{'cars'},
    # ── BIKES / SCOOTERS ─────────────────────────────────────────
    'bajaj':{'bikes','scooters'},'hero':{'bikes','scooters'},
    'royal enfield':{'bikes'},'yamaha':{'bikes','scooters'},
    'kawasaki':{'bikes'},'ktm':{'bikes'},'triumph':{'bikes'},
    'harley davidson':{'bikes'},'harley':{'bikes'},'jawa':{'bikes'},
    'tvs':{'bikes','scooters'},'revolt':{'bikes'},
    'cfmoto':{'bikes'},'benelli':{'bikes'},'yezdi':{'bikes'},
    'husqvarna':{'bikes'},'ducati':{'bikes'},'norton':{'bikes'},
    'indian':{'bikes'},'bmw motorrad':{'bikes'},
    'aprilia':{'bikes','scooters'},'vespa':{'scooters'},
    'ola':{'scooters'},'ather':{'scooters'},
    'pure ev':{'scooters','bikes'},'bgauss':{'scooters'},
    'ampere':{'scooters'},'okinawa':{'scooters'},
    'hero electric':{'scooters'},'simple energy':{'scooters'},
    'kabira':{'bikes','scooters'},'revolt':{'bikes'},
    'ultraviolette':{'bikes'},'matter':{'bikes'},
    'bounce infinity':{'scooters'},
    # ── TRUCKS / COMMERCIAL ───────────────────────────────────────
    'ashok leyland':{'trucks'},'eicher':{'trucks'},
    'force':{'trucks','cars'},'sml isuzu':{'trucks'},
    'bharat benz':{'trucks'},'man':{'trucks'},
    'scania':{'trucks'},'volvo trucks':{'trucks'},
    'piaggio':{'trucks','scooters'},'atul':{'trucks'},
    # ── TRACTORS ─────────────────────────────────────────────────
    'john deere':{'tractors'},'swaraj':{'tractors'},
    'sonalika':{'tractors'},'new holland':{'tractors'},
    'kubota':{'tractors'},'powertrac':{'tractors'},
    'captain tractors':{'tractors'},'massey ferguson':{'tractors'},
    'farmtrac':{'tractors'},'preet':{'tractors'},
    'indo farm':{'tractors'},'escorts':{'tractors'},
    'fieldking':{'tractors'},'hmt':{'tractors'},
    'vst':{'tractors'},'eicher tractor':{'tractors'},
    'ace':{'tractors'},'force tractor':{'tractors'},
}

KNOWN_VEHICLE_BRANDS = set(BRAND_VEHICLE_TYPES.keys())

TYPE_LABELS = {
    'cars':'Car / SUV','bikes':'Bike / Motorcycle',
    'scooters':'Scooter','trucks':'Truck / Commercial Vehicle',
    'tractors':'Tractor / Farm Equipment',
}

BRAND_CORRECTIONS = {
    'mercedez':'Mercedes','mercides':'Mercedes','merecedes':'Mercedes',
    'toyata':'Toyota','toyoto':'Toyota',
    'hundai':'Hyundai','hyndai':'Hyundai','hunday':'Hyundai',
    'maruthi':'Maruti','maruti suzuki':'Maruti',
    'kawasaky':'Kawasaki','yamha':'Yamaha','yammaha':'Yamaha',
    'royal enfeild':'Royal Enfield','royal enfild':'Royal Enfield',
    're':'Royal Enfield','r.e.':'Royal Enfield',
    'volksvagen':'Volkswagen','volkswagon':'Volkswagen',
    'harley davison':'Harley Davidson','tatta':'Tata',
    'bajaj auto':'Bajaj','hero motocorp':'Hero','hero honda':'Hero',
    'gm':'Chevrolet','general motors':'Chevrolet',
    'bmw bike':'BMW Motorrad','bmw moto':'BMW Motorrad',
    'al':'Ashok Leyland','john':'John Deere',
    'mf':'Massey Ferguson','jd':'John Deere',
}
MODEL_BELONGS_TO = {

    # ════════════════════════════════════════════════════════════════
    #  MARUTI SUZUKI  (every model ever sold in India)
    # ════════════════════════════════════════════════════════════════
    '800':'maruti','maruti 800':'maruti','ss80':'maruti',
    'omni':'maruti','omni cargo':'maruti','omni mpi':'maruti',
    'gypsy':'maruti','gypsy king':'maruti','gypsy ex':'maruti',
    'esteem':'maruti','esteem vxi':'maruti',
    'zen':'maruti','zen estilo':'maruti','estilo':'maruti',
    'wagon r':'maruti','wagonr':'maruti','wagon r stingray':'maruti',
    'wagon r cng':'maruti','wagon r flex fuel':'maruti',
    'alto':'maruti','alto 800':'maruti','alto k10':'maruti',
    'a-star':'maruti','astar':'maruti',
    'ritz':'maruti','ritz vxi':'maruti',
    'swift':'maruti','swift dzire':'maruti','swift vxi':'maruti',
    'swift zxi':'maruti','swift lxi':'maruti',
    'dzire':'maruti','dzire vxi':'maruti','dzire zxi':'maruti',
    'sx4':'maruti','sx4 zxi':'maruti',
    'kizashi':'maruti',
    'baleno':'maruti','baleno rs':'maruti','baleno sigma':'maruti',
    'baleno delta':'maruti','baleno zeta':'maruti','baleno alpha':'maruti',
    'celerio':'maruti','celerio x':'maruti','celerio cng':'maruti',
    'ignis':'maruti','ignis sigma':'maruti','ignis delta':'maruti',
    'brezza':'maruti','vitara brezza':'maruti','brezza cng':'maruti',
    'ertiga':'maruti','ertiga cng':'maruti','ertiga vxi':'maruti',
    'xl6':'maruti','xl6 cng':'maruti','xl6 alpha':'maruti',
    'ciaz':'maruti','ciaz sigma':'maruti','ciaz delta':'maruti',
    's-presso':'maruti','spresso':'maruti',
    'fronx':'maruti','fronx sigma':'maruti','fronx delta':'maruti',
    'jimny':'maruti','jimny zeta':'maruti','jimny alpha':'maruti',
    'grand vitara':'maruti','grand vitara sigma':'maruti',
    'invicto':'maruti','invicto zeta':'maruti',
    'eeco':'maruti','eeco cng':'maruti','eeco cargo':'maruti',
    'super carry':'maruti','carry':'maruti',
    'omni lpo':'maruti','versa':'maruti',
    'tour s':'maruti','tour v':'maruti','tour h3':'maruti',
    'tour h5':'maruti','tour m':'maruti','tour f':'maruti',
    'splash':'maruti',

    # ════════════════════════════════════════════════════════════════
    #  HYUNDAI
    # ════════════════════════════════════════════════════════════════
    'santro':'hyundai','santro xing':'hyundai',
    'eon':'hyundai','eon era':'hyundai','eon magna':'hyundai',
    'i10':'hyundai','grand i10':'hyundai','grand i10 nios':'hyundai',
    'i10 sportz':'hyundai','i10 magna':'hyundai',
    'i20':'hyundai','elite i20':'hyundai','i20 active':'hyundai',
    'i20 n line':'hyundai','i20 sportz':'hyundai','i20 asta':'hyundai',
    'aura':'hyundai','aura s':'hyundai','aura sx':'hyundai',
    'exter':'hyundai','exter s':'hyundai','exter sx':'hyundai',
    'venue':'hyundai','venue n line':'hyundai','venue s':'hyundai',
    'venue e':'hyundai','venue sx':'hyundai',
    'creta':'hyundai','creta e':'hyundai','creta s':'hyundai',
    'creta sx':'hyundai','creta n line':'hyundai',
    'creta electric':'hyundai','creta ev':'hyundai',
    'verna':'hyundai','verna sx':'hyundai','verna sxi':'hyundai',
    'verna fluidic':'hyundai','verna transform':'hyundai',
    'alcazar':'hyundai','alcazar prestige':'hyundai',
    'alcazar platinum':'hyundai',
    'tucson':'hyundai','new tucson':'hyundai',
    'ioniq 5':'hyundai','ioniq 6':'hyundai','ioniq 5 n':'hyundai',
    'kona electric':'hyundai','kona ev':'hyundai',
    'xcent':'hyundai','xcent prime':'hyundai',
    'accent':'hyundai','accent viva':'hyundai',
    'sonata':'hyundai','sonata transform':'hyundai',
    'terracan':'hyundai','getz':'hyundai',
    'i25':'hyundai','matrix':'hyundai',
    'starex':'hyundai','h1':'hyundai',
    'staria':'hyundai','h350':'hyundai',

    # ════════════════════════════════════════════════════════════════
    #  TATA MOTORS
    # ════════════════════════════════════════════════════════════════
    'nano':'tata','nano twist':'tata','nano lx':'tata',
    'indica':'tata','indica v2':'tata','indica vista':'tata',
    'indigo':'tata','indigo cs':'tata','indigo manza':'tata',
    'manza':'tata','zest':'tata','bolt':'tata',
    'tiago':'tata','tiago jtp':'tata','tiago cng':'tata',
    'tiago ev':'tata','tiago nrg':'tata',
    'tigor':'tata','tigor ev':'tata','tigor sport':'tata',
    'altroz':'tata','altroz cng':'tata','altroz racer':'tata',
    'altroz dark':'tata','altroz i-turbo':'tata',
    'punch':'tata','punch cng':'tata','punch ev':'tata',
    'punch icng':'tata','punch adventure':'tata',
    'nexon':'tata','nexon ev':'tata','nexon ev max':'tata',
    'nexon ev prime':'tata','nexon dark':'tata',
    'harrier':'tata','harrier xz':'tata','harrier dark':'tata',
    'harrier ev':'tata',
    'safari':'tata','safari dicor':'tata','new safari':'tata',
    'safari xz':'tata','safari adventure persona':'tata',
    'safari ev':'tata',
    'curvv':'tata','curvv ev':'tata','curvv coupe ev':'tata',
    'sierra ev':'tata','avinya':'tata','acti.ev':'tata',
    'hexa':'tata','aria':'tata','sumo':'tata',
    'sumo victa':'tata','sumo gold':'tata','grande mk2':'tata',
    'venture':'tata','movus':'tata','xenon':'tata',
    'xylo':'tata',
    # Tata Commercial
    'ace':'tata','tata ace':'tata','ace ev':'tata',
    'super ace':'tata','ace zip':'tata','ace gold':'tata',
    'intra v10':'tata','intra v30':'tata',
    'yodha':'tata','yodha 2.0':'tata',
    'xenon yodha':'tata','tata magic':'tata',
    'tata winger':'tata','magic iris':'tata',
    '407':'tata','tata 407':'tata','407 gold':'tata',
    '709':'tata','tata 709':'tata','709 lpt':'tata',
    '909 lpt':'tata','1109':'tata','1210':'tata',
    '1512 lpt':'tata','1616 lpt':'tata',
    '2518 lpt':'tata','3518 lpt':'tata',
    'prima':'tata','prima 3525':'tata','prima 4928':'tata',
    'signa':'tata','signa 2818':'tata','signa 4625':'tata',
    'ultra':'tata','ultra t7':'tata','ultra 614':'tata',
    'star bus':'tata','starbus ultra':'tata',
    'lpk 2518':'tata','lpt 3118':'tata',

    # ════════════════════════════════════════════════════════════════
    #  HONDA  (Cars + Bikes + Scooters)
    # ════════════════════════════════════════════════════════════════
    # Cars
    'brio':'honda','brio s':'honda',
    'amaze':'honda','amaze s':'honda','amaze v':'honda',
    'city':'honda','city zx':'honda','city s':'honda',
    'city hybrid':'honda','city e hev':'honda',
    'jazz':'honda','jazz s':'honda','jazz v':'honda',
    'wr-v':'honda','wrv':'honda','wr-v s':'honda',
    'elevate':'honda','elevate v':'honda','elevate zx':'honda',
    'cr-v':'honda','crv':'honda','br-v':'honda',
    'mobilio':'honda','accord':'honda',
    'civic':'honda','freed':'honda',
    # Bikes
    'cd 70':'honda','cd 100':'honda','cd 110 dream':'honda',
    'dream yuga':'honda','dream neo':'honda','dream 110':'honda',
    'shine 100':'honda','shine':'honda','honda shine':'honda',
    'shine sp':'honda','shine dlx':'honda',
    'sp 125':'honda','sp125':'honda','sp 125 ble':'honda',
    'unicorn':'honda','unicorn 160':'honda','unicorn dazzler':'honda',
    'hornet':'honda','hornet 2.0':'honda','cb hornet 160r':'honda',
    'x-blade':'honda','xblade':'honda',
    'cb300r':'honda','cb300':'honda',
    'cb350':'honda','cb350rs':'honda','cb350r':'honda',
    'h ness cb350':'honda','cb 350 h ness':'honda',
    'cb500f':'honda','cb500x':'honda',
    'cbr 500r':'honda','cbr500r':'honda',
    'cbr 650r':'honda','cbr650r':'honda',
    'cbr 250r':'honda','cbr250r':'honda',
    'cbr 1000rr':'honda','cbr 600rr':'honda',
    'africa twin':'honda','crf 1100l':'honda',
    'goldwing':'honda','gl1800':'honda',
    'rebel 500':'honda','rebel 1100':'honda',
    'shadow 750':'honda','fury':'honda',
    'nt 1100':'honda','nc 750x':'honda',
    # Scooters
    'activa':'honda','activa 6g':'honda','activa 125':'honda',
    'activa 5g':'honda','activa 4g':'honda','activa i':'honda',
    'dio':'honda','new dio':'honda','dio dlx':'honda',
    'grazia':'honda','grazia dlx':'honda',
    'aviator':'honda','navi':'honda','cliq':'honda',
    'destini 125 honda':'honda',
    'metropolitan':'honda',

    # ════════════════════════════════════════════════════════════════
    #  TOYOTA
    # ════════════════════════════════════════════════════════════════
    'qualis':'toyota','qualis ls':'toyota',
    'etios':'toyota','etios liva':'toyota','etios cross':'toyota',
    'etios valco':'toyota','etios sedan':'toyota',
    'glanza':'toyota','glanza s':'toyota','glanza v':'toyota',
    'urban cruiser':'toyota','urban cruiser hyryder':'toyota',
    'hyryder':'toyota','hyryder s':'toyota','hyryder v':'toyota',
    'innova':'toyota','innova crysta':'toyota',
    'innova hycross':'toyota','innova hycross vx':'toyota',
    'fortuner':'toyota','fortuner sigma4':'toyota',
    'fortuner legender':'toyota','fortuner 4x4':'toyota',
    'camry':'toyota','camry hybrid':'toyota',
    'vellfire':'toyota','alphard':'toyota',
    'hilux':'toyota','hilux adventure':'toyota',
    'land cruiser':'toyota','land cruiser 200':'toyota',
    'land cruiser 300':'toyota','lc 300':'toyota',
    'prado':'toyota','land cruiser prado':'toyota',
    'corolla':'toyota','corolla altis':'toyota',
    'corolla suites':'toyota','corolla hybrid':'toyota',
    'yaris':'toyota','rush':'toyota',
    'raize':'toyota','agya':'toyota','sienta':'toyota',
    'hiace':'toyota','granvia':'toyota',

    # ════════════════════════════════════════════════════════════════
    #  MAHINDRA  (Cars + Trucks + Tractors)
    # ════════════════════════════════════════════════════════════════
    # Cars
    'mm 540':'mahindra','mm 550':'mahindra','mm 775':'mahindra',
    'armada':'mahindra','commander':'mahindra','marshal':'mahindra',
    'bolero':'mahindra','bolero neo':'mahindra','bolero plus':'mahindra',
    'bolero power plus':'mahindra','bolero b4':'mahindra',
    'scorpio':'mahindra','scorpio classic':'mahindra',
    'scorpio n':'mahindra','scorpio s3':'mahindra','scorpio s5':'mahindra',
    'scorpio s7':'mahindra','scorpio s9':'mahindra','scorpio s11':'mahindra',
    'thar':'mahindra','thar ax':'mahindra','thar lx':'mahindra',
    'thar roxx':'mahindra','thar 4x4':'mahindra',
    'xuv300':'mahindra','xuv 300':'mahindra','xuv300 w4':'mahindra',
    'xuv300 w6':'mahindra','xuv300 w8':'mahindra',
    'xuv400':'mahindra','xuv 400':'mahindra','xuv400 ec':'mahindra',
    'xuv400 el':'mahindra',
    'xuv500':'mahindra','xuv 500':'mahindra',
    'xuv700':'mahindra','xuv 700':'mahindra','xuv700 ax5':'mahindra',
    'xuv700 ax7':'mahindra','xuv700 mx':'mahindra',
    'xuv 3xo':'mahindra','xuv3xo':'mahindra',
    'marazzo':'mahindra','marazzo m2':'mahindra','marazzo m6':'mahindra',
    'alturas g4':'mahindra','alturas':'mahindra',
    'rexton':'mahindra','ssangyong rexton':'mahindra',
    'kuv100':'mahindra','kuv100 nxt':'mahindra',
    'verito':'mahindra','verito vibe':'mahindra',
    'nuvosport':'mahindra','tuv300':'mahindra','tuv300 plus':'mahindra',
    'quanto':'mahindra',
    'e20':'mahindra','e20 plus':'mahindra','e2o':'mahindra',
    'e-verito':'mahindra','reva':'mahindra',
    'be 6e':'mahindra','be6e':'mahindra','be 9e':'mahindra',
    'xe 9e':'mahindra',
    'oja 2121':'mahindra','oja 3140':'mahindra',
    # Trucks
    'bolero pickup':'mahindra','bolero maxi truck':'mahindra',
    'bolero camper':'mahindra',
    'jeeto':'mahindra','jeeto s':'mahindra','jeeto plus':'mahindra',
    'supro':'mahindra','supro profit truck':'mahindra',
    'supro mini truck':'mahindra',
    'alfa load':'mahindra','alfa passenger':'mahindra',
    'treo auto':'mahindra','treo yaari':'mahindra',
    'e-alfa mini':'mahindra',
    'blazo 35':'mahindra','blazo 37':'mahindra',
    'blazo 49':'mahindra','blazo x 28':'mahindra',
    'furio 7':'mahindra','furio 9':'mahindra',
    'furio 11':'mahindra','furio 12':'mahindra',
    'furio 14':'mahindra','furio 17':'mahindra',
    'truxo':'mahindra',
    'scorpio pick up':'mahindra',
    # Tractors
    'mahindra 265':'mahindra','mahindra 275':'mahindra',
    'mahindra 475':'mahindra','mahindra 575':'mahindra',
    'mahindra 605':'mahindra','mahindra 615':'mahindra',
    'mahindra 625':'mahindra','mahindra 635':'mahindra',
    'mahindra 645':'mahindra','mahindra 655':'mahindra',
    'mahindra 665':'mahindra','mahindra 755':'mahindra',
    'mahindra 765':'mahindra','mahindra 775':'mahindra',
    'arjun 555':'mahindra','arjun 605':'mahindra',
    'arjun 605 di ms':'mahindra','arjun 755':'mahindra',
    'arjun novo':'mahindra','arjun 555 di':'mahindra',
    'yuvo 575':'mahindra','yuvo 585':'mahindra',
    'yuvo 605':'mahindra','yuvo 275':'mahindra',
    'novo 605':'mahindra','novo 655':'mahindra',
    'jivo 245':'mahindra','jivo 225':'mahindra',
    'sarpanch plus':'mahindra',

    # ════════════════════════════════════════════════════════════════
    #  KIA
    # ════════════════════════════════════════════════════════════════
    'seltos':'kia','seltos htx':'kia','seltos gtx':'kia',
    'sonet':'kia','sonet htx':'kia','sonet gtx':'kia',
    'carens':'kia','carens prestige':'kia','carens luxury':'kia',
    'ev6':'kia','ev6 gt':'kia','ev6 gt line':'kia',
    'ev9':'kia',
    'carnival':'kia','carnival limousine':'kia',
    'sportage':'kia','sorento':'kia','stinger':'kia',
    'niro':'kia','niro ev':'kia','stonic':'kia',
    'picanto':'kia',

    # ════════════════════════════════════════════════════════════════
    #  VOLKSWAGEN
    # ════════════════════════════════════════════════════════════════
    'polo':'volkswagen','cross polo':'volkswagen',
    'polo gt tsi':'volkswagen','polo gt tdi':'volkswagen',
    'vento':'volkswagen','vento comfortline':'volkswagen',
    'ameo':'volkswagen','ameo comfortline':'volkswagen',
    'taigun':'volkswagen','taigun comfortline':'volkswagen',
    'taigun highline':'volkswagen','taigun topline':'volkswagen',
    'virtus':'volkswagen','virtus dynamic':'volkswagen',
    'virtus performance':'volkswagen',
    'tiguan':'volkswagen','tiguan allspace':'volkswagen',
    'passat':'volkswagen','jetta':'volkswagen',
    'golf':'volkswagen','golf gti':'volkswagen',
    't-roc':'volkswagen','t-cross':'volkswagen',
    'touareg':'volkswagen','id.4':'volkswagen',
    'id.3':'volkswagen','id.5':'volkswagen',

    # ════════════════════════════════════════════════════════════════
    #  SKODA
    # ════════════════════════════════════════════════════════════════
    'fabia':'skoda','fabia rs':'skoda',
    'rapid':'skoda','rapid rider':'skoda',
    'octavia':'skoda','octavia rs':'skoda','octavia l&k':'skoda',
    'octavia combi':'skoda','octavia scout':'skoda',
    'superb':'skoda','superb l&k':'skoda','superb combi':'skoda',
    'yeti':'skoda','yeti outdoor':'skoda',
    'kushaq':'skoda','kushaq monte carlo':'skoda',
    'slavia':'skoda','slavia monte carlo':'skoda',
    'kodiaq':'skoda','kodiaq scout':'skoda','kodiaq l&k':'skoda',
    'karoq':'skoda','citigo':'skoda',
    'enyaq':'skoda','scala':'skoda','kamiq':'skoda',

    # ════════════════════════════════════════════════════════════════
    #  RENAULT
    # ════════════════════════════════════════════════════════════════
    'kwid':'renault','kwid rxe':'renault','kwid rxl':'renault',
    'kwid rxt':'renault','kwid climber':'renault',
    'kiger':'renault','kiger rxe':'renault','kiger rxl':'renault',
    'kiger rxz':'renault','kiger rxz turbo':'renault',
    'triber':'renault','triber rxe':'renault','triber rxl':'renault',
    'triber rxz':'renault',
    'duster':'renault','duster rxe':'renault','duster rxl':'renault',
    'duster rxz':'renault','duster awd':'renault',
    'lodgy':'renault','captur':'renault',
    'fluence':'renault','koleos':'renault',
    'pulse':'renault','scala':'renault',
    'zoe':'renault','megane':'renault',

    # ════════════════════════════════════════════════════════════════
    #  NISSAN
    # ════════════════════════════════════════════════════════════════
    'magnite':'nissan','magnite xe':'nissan','magnite xv':'nissan',
    'magnite xv premium':'nissan',
    'micra':'nissan','micra active':'nissan',
    'sunny':'nissan','sunny xl':'nissan',
    'terrano':'nissan','terrano xl':'nissan','terrano xv':'nissan',
    'kicks':'nissan','kicks xv':'nissan',
    'x-trail':'nissan','evalia':'nissan',
    'leaf':'nissan','ariya':'nissan',
    'patrol':'nissan','navara':'nissan',

    # ════════════════════════════════════════════════════════════════
    #  MG MOTOR
    # ════════════════════════════════════════════════════════════════
    'hector':'mg','hector plus':'mg','hector sharp':'mg',
    'hector 5-seater':'mg','hector 6-seater':'mg',
    'astor':'mg','astor style':'mg','astor sharp':'mg',
    'gloster':'mg','gloster sharp':'mg','gloster savvy':'mg',
    'zs ev':'mg','zs ev excite':'mg','zs ev exclusive':'mg',
    'comet ev':'mg','windsor ev':'mg','windsor':'mg',
    'cyberster':'mg','extender':'mg',
    'mg one':'mg','mg5':'mg','mg6':'mg',

    # ════════════════════════════════════════════════════════════════
    #  JEEP
    # ════════════════════════════════════════════════════════════════
    'compass':'jeep','compass sport':'jeep','compass longitude':'jeep',
    'compass limited':'jeep','compass trailhawk':'jeep',
    'meridian':'jeep','meridian x':'jeep','meridian limited':'jeep',
    'wrangler':'jeep','wrangler rubicon':'jeep','wrangler sahara':'jeep',
    'wrangler unlimited':'jeep',
    'grand cherokee':'jeep','grand cherokee l':'jeep',
    'renegade':'jeep','commander':'jeep',
    'gladiator':'jeep','cherokee':'jeep',

    # ════════════════════════════════════════════════════════════════
    #  FORD
    # ════════════════════════════════════════════════════════════════
    'ikon':'ford','ikon nxt':'ford','ikon flair':'ford',
    'fiesta':'ford','fiesta classic':'ford',
    'figo':'ford','figo aspire':'ford','aspire':'ford',
    'freestyle':'ford','ecosport':'ford','ecosport trend':'ford',
    'ecosport titanium':'ford',
    'endeavour':'ford','endeavour sport':'ford','endeavour titanium':'ford',
    'mustang':'ford','mustang gt':'ford','mustang mach e':'ford',
    'ranger':'ford','f-150':'ford',
    'transit':'ford','transit custom':'ford',
    'fusion':'ford','mondeo':'ford',

    # ════════════════════════════════════════════════════════════════
    #  CHEVROLET / GM
    # ════════════════════════════════════════════════════════════════
    'spark':'chevrolet','beat':'chevrolet','beat lt':'chevrolet',
    'beat ls':'chevrolet',
    'sail':'chevrolet','sail hatchback':'chevrolet',
    'cruze':'chevrolet','cruze lt':'chevrolet',
    'enjoy':'chevrolet','enjoy lt':'chevrolet',
    'tavera':'chevrolet','tavera neo':'chevrolet',
    'captiva':'chevrolet','trailblazer':'chevrolet',
    'optra':'chevrolet',

    # ════════════════════════════════════════════════════════════════
    #  FIAT
    # ════════════════════════════════════════════════════════════════
    'palio':'fiat','palio nv':'fiat','palio adventure':'fiat',
    'punto':'fiat','grande punto':'fiat','punto evo':'fiat',
    'linea':'fiat','linea classic':'fiat','linea t-jet':'fiat',
    'avventura':'fiat','urban cross':'fiat',

    # ════════════════════════════════════════════════════════════════
    #  CITROEN
    # ════════════════════════════════════════════════════════════════
    'c3':'citroen','c3 you':'citroen','c3 feel':'citroen',
    'c3 shine':'citroen',
    'c3 aircross':'citroen','ec3':'citroen',
    'c5 aircross':'citroen','c5 aircross feel':'citroen',
    'berlingo':'citroen',

    # ════════════════════════════════════════════════════════════════
    #  DATSUN
    # ════════════════════════════════════════════════════════════════
    'go':'datsun','go plus':'datsun','redi-go':'datsun',
    'redi go':'datsun',

    # ════════════════════════════════════════════════════════════════
    #  ISUZU
    # ════════════════════════════════════════════════════════════════
    'd-max':'isuzu','d max':'isuzu','d-max vcross':'isuzu',
    'mu-x':'isuzu','mu x':'isuzu','mux':'isuzu',
    'traga':'isuzu',

    # ════════════════════════════════════════════════════════════════
    #  BMW  (Cars)
    # ════════════════════════════════════════════════════════════════
    '1 series':'bmw','2 series':'bmw','2 series gran coupe':'bmw',
    '3 series':'bmw','3 series gt':'bmw',
    '4 series':'bmw','4 series gran coupe':'bmw',
    '5 series':'bmw','6 series':'bmw','6 series gt':'bmw',
    '7 series':'bmw','8 series':'bmw',
    'x1':'bmw','x2':'bmw','x3':'bmw','x4':'bmw',
    'x5':'bmw','x6':'bmw','x7':'bmw',
    'x3 m':'bmw','x4 m':'bmw','x5 m':'bmw','x6 m':'bmw',
    'z4':'bmw','m2':'bmw','m3':'bmw','m4':'bmw',
    'm5':'bmw','m6':'bmw','m8':'bmw',
    'i3':'bmw','i4':'bmw','i5':'bmw','i7':'bmw','i8':'bmw',
    'ix':'bmw','ix3':'bmw','ix1':'bmw','ix2':'bmw',
    'alpina':'bmw',

    # ════════════════════════════════════════════════════════════════
    #  MERCEDES-BENZ
    # ════════════════════════════════════════════════════════════════
    'a class':'mercedes','a 180':'mercedes','a 200':'mercedes',
    'a 220':'mercedes','a 45 amg':'mercedes',
    'b class':'mercedes','b 200':'mercedes',
    'c class':'mercedes','c 180':'mercedes','c 200':'mercedes',
    'c 300':'mercedes','c 43 amg':'mercedes','c 63 amg':'mercedes',
    'e class':'mercedes','e 200':'mercedes','e 300':'mercedes',
    'e 400':'mercedes','e 220d':'mercedes',
    's class':'mercedes','s 400':'mercedes','s 450':'mercedes',
    's 500':'mercedes','s 580':'mercedes','s 680':'mercedes',
    'gla':'mercedes','gla 200':'mercedes','gla 220d':'mercedes',
    'glb':'mercedes','glb 200':'mercedes',
    'glc':'mercedes','glc 200':'mercedes','glc 300':'mercedes',
    'glc 43 amg':'mercedes',
    'gle':'mercedes','gle 300d':'mercedes','gle 450':'mercedes',
    'gle 53 amg':'mercedes',
    'gls':'mercedes','gls 400d':'mercedes','gls 450':'mercedes',
    'g class':'mercedes','g 350d':'mercedes','g 500':'mercedes',
    'g 63 amg':'mercedes','g wagon':'mercedes',
    'cla':'mercedes','cla 200':'mercedes','cla 250':'mercedes',
    'cls':'mercedes','cls 300':'mercedes',
    'sl':'mercedes','sl 55 amg':'mercedes','sl 63 amg':'mercedes',
    'amg gt':'mercedes','amg one':'mercedes',
    'eqa':'mercedes','eqb':'mercedes','eqc':'mercedes',
    'eqe':'mercedes','eqs':'mercedes','eqa 250':'mercedes',
    'v class':'mercedes','v 220d':'mercedes',
    'maybach s 580':'mercedes','maybach gls 600':'mercedes',
    'sprinter':'mercedes','vito':'mercedes',

    # ════════════════════════════════════════════════════════════════
    #  AUDI
    # ════════════════════════════════════════════════════════════════
    'a1':'audi','a1 sportback':'audi',
    'a3':'audi','a3 sedan':'audi','a3 sportback':'audi',
    'a4':'audi','a4 allroad':'audi',
    'a5':'audi','a5 sportback':'audi','a5 cabriolet':'audi',
    'a6':'audi','a6 allroad':'audi',
    'a7':'audi','a7 sportback':'audi',
    'a8':'audi','a8l':'audi',
    'q2':'audi','q3':'audi','q3 sportback':'audi',
    'q5':'audi','q5 sportback':'audi',
    'q7':'audi','q8':'audi','q8 sportback':'audi',
    'q4 e-tron':'audi','q8 e-tron':'audi',
    'r8':'audi','r8 v10':'audi',
    'tt':'audi','tt coupe':'audi','tt roadster':'audi','tts':'audi',
    's3':'audi','s4':'audi','s5':'audi',
    's6':'audi','s7':'audi','s8':'audi',
    'rs3':'audi','rs5':'audi','rs6':'audi',
    'rs7':'audi','rs q8':'audi',
    'e-tron gt':'audi','rs e-tron gt':'audi',
    'e-tron s':'audi','e-tron sportback':'audi',

    # ════════════════════════════════════════════════════════════════
    #  LAND ROVER / RANGE ROVER
    # ════════════════════════════════════════════════════════════════
    'defender':'land rover','defender 90':'land rover',
    'defender 110':'land rover','defender 130':'land rover',
    'discovery':'land rover','discovery sport':'land rover',
    'discovery 3':'land rover','discovery 4':'land rover',
    'discovery 5':'land rover','freelander':'land rover',
    'freelander 2':'land rover',
    'range rover':'land rover','range rover sport':'land rover',
    'range rover evoque':'land rover','range rover velar':'land rover',
    'range rover sv':'land rover',
    'range rover autobiography':'land rover',

    # ════════════════════════════════════════════════════════════════
    #  LEXUS
    # ════════════════════════════════════════════════════════════════
    'es 300h':'lexus','es300h':'lexus','ls 500h':'lexus',
    'lx 500d':'lexus','lx 570':'lexus',
    'rx 450h':'lexus','rx 350':'lexus',
    'nx 350h':'lexus','nx 300':'lexus',
    'ux 300e':'lexus','lc 500':'lexus',

    # ════════════════════════════════════════════════════════════════
    #  PORSCHE
    # ════════════════════════════════════════════════════════════════
    '718 boxster':'porsche','718 cayman':'porsche','718 spyder':'porsche',
    '911':'porsche','911 carrera':'porsche','911 targa':'porsche',
    '911 turbo':'porsche','911 gt3':'porsche','911 gt3 rs':'porsche',
    'panamera':'porsche','panamera 4s':'porsche','panamera turbo':'porsche',
    'panamera sport turismo':'porsche',
    'cayenne':'porsche','cayenne coupe':'porsche',
    'cayenne gts':'porsche','cayenne turbo':'porsche',
    'macan':'porsche','macan s':'porsche','macan gts':'porsche',
    'macan turbo':'porsche','macan ev':'porsche',
    'taycan':'porsche','taycan 4s':'porsche','taycan turbo':'porsche',
    'taycan turbo s':'porsche','taycan sport turismo':'porsche',
    'taycan cross turismo':'porsche',

    # ════════════════════════════════════════════════════════════════
    #  VOLVO
    # ════════════════════════════════════════════════════════════════
    'xc40':'volvo','xc40 recharge':'volvo',
    'xc60':'volvo','xc60 inscription':'volvo',
    'xc90':'volvo','xc90 inscription':'volvo',
    's60':'volvo','s90':'volvo','s90 inscription':'volvo',
    'v60':'volvo','v90':'volvo','c40 recharge':'volvo',

    # ════════════════════════════════════════════════════════════════
    #  MITSUBISHI
    # ════════════════════════════════════════════════════════════════
    'lancer':'mitsubishi','lancer evo':'mitsubishi',
    'galant':'mitsubishi','cedia':'mitsubishi',
    'outlander':'mitsubishi','outlander phev':'mitsubishi',
    'montero':'mitsubishi','pajero':'mitsubishi',
    'pajero sport':'mitsubishi','triton':'mitsubishi',
    'eclipse cross':'mitsubishi','asx':'mitsubishi',
    'l200':'mitsubishi',

    # ════════════════════════════════════════════════════════════════
    #  MINI
    # ════════════════════════════════════════════════════════════════
    'hatch':'mini','convertible':'mini',
    'clubman':'mini','countryman':'mini',
    'paceman':'mini','coupe':'mini',
    'roadster':'mini','mini cooper':'mini',
    'mini john cooper works':'mini',
    'mini electric':'mini',

    # ════════════════════════════════════════════════════════════════
    #  BAJAJ  (complete)
    # ════════════════════════════════════════════════════════════════
    # Commuters
    'ct 100':'bajaj','ct100':'bajaj','ct 100b':'bajaj',
    'ct 110':'bajaj','ct110':'bajaj','ct 110x':'bajaj',
    'platina 100':'bajaj','platina 110':'bajaj',
    'platina 110 h gear':'bajaj','platina':'bajaj',
    'boxer':'bajaj','kb100':'bajaj','kb125':'bajaj',
    'byk':'bajaj','wave':'bajaj','wind 125':'bajaj',
    'classic':'bajaj',
    # Discover
    'discover 100':'bajaj','discover 110':'bajaj',
    'discover 125':'bajaj','discover 125 st':'bajaj',
    'discover 125m':'bajaj','discover 150':'bajaj',
    'discover 150f':'bajaj','discover 150s':'bajaj',
    'discover':'bajaj',
    # Pulsar
    'pulsar 125':'bajaj','pulsar 125 neon':'bajaj',
    'pulsar 150':'bajaj','pulsar 150 neon':'bajaj',
    'pulsar 160 ns':'bajaj','pulsar ns 160':'bajaj','pulsar ns160':'bajaj',
    'pulsar 180':'bajaj','pulsar 180f':'bajaj',
    'pulsar 200 ns':'bajaj','pulsar ns 200':'bajaj','pulsar ns200':'bajaj',
    'pulsar n250':'bajaj','pulsar n 250':'bajaj',
    'pulsar f250':'bajaj','pulsar f 250':'bajaj',
    'pulsar ns 400':'bajaj','pulsar ns400':'bajaj',
    'pulsar 220f':'bajaj','pulsar 220':'bajaj',
    'pulsar rs200':'bajaj','pulsar rs 200':'bajaj',
    'rs200':'bajaj','rs 200':'bajaj',
    'ns200':'bajaj','ns 200':'bajaj',
    'ns400':'bajaj','ns 400':'bajaj',
    'n250':'bajaj','f250':'bajaj',
    'p150':'bajaj','freedom 125':'bajaj',
    # Dominar
    'dominar 250':'bajaj','dominar 400':'bajaj','dominar':'bajaj',
    # Avenger
    'avenger 160':'bajaj','avenger 220':'bajaj',
    'avenger street 160':'bajaj','avenger street 220':'bajaj',
    'avenger cruise 220':'bajaj','avenger':'bajaj',
    # Chetak
    'chetak':'bajaj','chetak electric':'bajaj',
    'chetak premium':'bajaj','chetak urbane':'bajaj',

    # ════════════════════════════════════════════════════════════════
    #  HERO MOTOCORP  (complete)
    # ════════════════════════════════════════════════════════════════
    'cd 100':'hero','hf100':'hero','hf dawn':'hero',
    'hf deluxe':'hero','hf deluxe i3s':'hero',
    'cd deluxe':'hero','cd 110 dream':'hero',
    'splendor plus':'hero','splendor pro':'hero',
    'splendor ismart':'hero','super splendor':'hero',
    'splendor xtec':'hero','splendor':'hero',
    'passion pro':'hero','passion xpro':'hero',
    'passion pro xtec':'hero','passion':'hero',
    'glamour':'hero','glamour xtec':'hero',
    'glamour programmed fi':'hero',
    'xtreme 160r':'hero','xtreme 200r':'hero',
    'xtreme 200s':'hero','xtreme 160s':'hero',
    'xtreme 125r':'hero','xtreme':'hero',
    'xpulse 200':'hero','xpulse 200t':'hero',
    'xpulse 200 4v':'hero','xpulse':'hero',
    'mavrick 440':'hero','mavrick':'hero',
    'cbz xtreme':'hero','cbz star':'hero','cbz':'hero',
    'hunk':'hero','hunk sport':'hero',
    'karizma r':'hero','karizma zmr':'hero','karizma':'hero',
    'ignitor':'hero','achiever':'hero',
    'thriller 160r':'hero','havoc 210':'hero',
    'duet':'hero','destini 125':'hero','destini 125 xtec':'hero',
    'pleasure plus':'hero','pleasure xtec':'hero','pleasure':'hero',
    'maestro edge 110':'hero','maestro edge 125':'hero',
    'maestro edge':'hero','maestro':'hero',
    'xoom':'hero','xoom 110':'hero',
    'vida v1':'hero','vida v1 plus':'hero','vida v1 pro':'hero',

    # ════════════════════════════════════════════════════════════════
    #  ROYAL ENFIELD  (complete)
    # ════════════════════════════════════════════════════════════════
    # Bullet
    'bullet 350':'royal enfield','bullet 350 es':'royal enfield',
    'bullet 500':'royal enfield','bullet 500 es':'royal enfield',
    'bullet machismo':'royal enfield','bullet':'royal enfield',
    # Classic
    'classic 350':'royal enfield','classic 350s':'royal enfield',
    'classic 500':'royal enfield','classic chrome':'royal enfield',
    'classic signals':'royal enfield','classic dark':'royal enfield',
    'classic':'royal enfield',
    # Thunderbird
    'thunderbird 350':'royal enfield','thunderbird 500':'royal enfield',
    'thunderbird x 350':'royal enfield','thunderbird x 500':'royal enfield',
    'thunderbird':'royal enfield',
    # Meteor
    'meteor 350':'royal enfield','meteor 350 fireball':'royal enfield',
    'meteor 350 stellar':'royal enfield','meteor':'royal enfield',
    # Hunter
    'hunter 350':'royal enfield','hunter 350 dapper':'royal enfield',
    'hunter 350 metro':'royal enfield','hunter':'royal enfield',
    # Himalayan
    'himalayan 411':'royal enfield','himalayan 450':'royal enfield',
    'himalayan':'royal enfield',
    # Scram
    'scram 411':'royal enfield','scram':'royal enfield',
    # 650 Twins
    'interceptor 650':'royal enfield','interceptor':'royal enfield',
    'continental gt 650':'royal enfield','continental gt':'royal enfield',
    'super meteor 650':'royal enfield','super meteor':'royal enfield',
    'shotgun 650':'royal enfield','shotgun':'royal enfield',
    # 450 Series
    'guerrilla 450':'royal enfield','guerrilla':'royal enfield',
    # Others
    'trials 350':'royal enfield','trials 500':'royal enfield',
    'electra':'royal enfield','electra x':'royal enfield',
    'flying flea c6':'royal enfield','flying flea s6':'royal enfield',
    'bear 650':'royal enfield','classic 650':'royal enfield',

    # ════════════════════════════════════════════════════════════════
    #  YAMAHA  (complete)
    # ════════════════════════════════════════════════════════════════
    # Commuters / entry
    'rx 100':'yamaha','rx100':'yamaha','rx 135':'yamaha','rd 350':'yamaha',
    'ybr 110':'yamaha','ybr 125':'yamaha','ybr 250':'yamaha',
    'saluto':'yamaha','saluto rx':'yamaha','saluto 125':'yamaha',
    # FZ series
    'fz fi':'yamaha','fz-fi':'yamaha','fz v2':'yamaha','fz v3':'yamaha',
    'fzs fi':'yamaha','fzs-fi':'yamaha','fzs v2':'yamaha','fzs v3':'yamaha',
    'fz-x':'yamaha','fz25':'yamaha','fz 25':'yamaha',
    'fazer 25':'yamaha','fazer fi v2':'yamaha',
    # MT series
    'mt-15':'yamaha','mt15':'yamaha','mt-03':'yamaha',
    'mt-07':'yamaha','mt-09':'yamaha','mt-10':'yamaha','mt-125':'yamaha',
    # R series
    'r15 v3':'yamaha','r15 v4':'yamaha','r15m':'yamaha',
    'r15':'yamaha','yzf r15':'yamaha',
    'r3':'yamaha','r7':'yamaha','r1':'yamaha','r1m':'yamaha',
    'yzf r3':'yamaha','yzf r7':'yamaha',
    # XSR
    'xsr155':'yamaha','xsr700':'yamaha','xsr900':'yamaha',
    # Adventure
    'tenere 700':'yamaha','tracer 9':'yamaha','tracer 7':'yamaha',
    # Cruiser
    'bolt':'yamaha','v-star':'yamaha','vmax':'yamaha','v-max':'yamaha',
    # Scooters
    'fascino':'yamaha','fascino 125':'yamaha','fascino fi':'yamaha',
    'ray zr':'yamaha','ray zr 125':'yamaha','ray zr street rally':'yamaha',
    'aerox 155':'yamaha','aerox':'yamaha',
    'nmax':'yamaha','xmax':'yamaha','tmax':'yamaha',

    # ════════════════════════════════════════════════════════════════
    #  TVS  (complete)
    # ════════════════════════════════════════════════════════════════
    # Commuters
    'xl 100':'tvs','xl 100 heavy duty':'tvs','xl super':'tvs',
    'sport':'tvs','tvs sport':'tvs','max 100':'tvs','max 100r':'tvs',
    'star city plus':'tvs','star city':'tvs','star sport':'tvs',
    'centra':'tvs','victor':'tvs','victor glx':'tvs',
    'radeon':'tvs','radeon special edition':'tvs',
    # Raider
    'raider 125':'tvs','raider':'tvs',
    # Ronin
    'ronin 225':'tvs','ronin':'tvs',
    # Apache
    'apache rtr 160':'tvs','apache rtr 160 4v':'tvs',
    'apache rtr 200 4v':'tvs','apache rtr 200':'tvs',
    'apache rr 310':'tvs','apache rr310':'tvs',
    'apache':'tvs',
    # Scooters
    'ntorq 125':'tvs','ntorq 125 race edition':'tvs','ntorq':'tvs',
    'jupiter 125':'tvs','jupiter classic':'tvs','jupiter':'tvs',
    'iqube st':'tvs','iqube s':'tvs','iqube':'tvs',
    'wego':'tvs','wego 110':'tvs',
    'scooty zest 110':'tvs','scooty pep plus':'tvs',
    'scooty pep+':'tvs','scooty streak':'tvs','scooty':'tvs',
    # 3-wheelers
    'king duramax':'tvs','king deluxe':'tvs',
    'cargo king':'tvs','three wheeler king':'tvs',

    # ════════════════════════════════════════════════════════════════
    #  KTM  (complete)
    # ════════════════════════════════════════════════════════════════
    'duke 125':'ktm','ktm 125 duke':'ktm','125 duke':'ktm',
    'duke 200':'ktm','ktm 200 duke':'ktm','200 duke':'ktm',
    'duke 250':'ktm','ktm 250 duke':'ktm','250 duke':'ktm',
    'duke 390':'ktm','ktm 390 duke':'ktm','390 duke':'ktm',
    '790 duke':'ktm','890 duke':'ktm',
    '1290 super duke r':'ktm','1290 super duke gt':'ktm',
    'rc 125':'ktm','rc125':'ktm','125 rc':'ktm',
    'rc 200':'ktm','rc200':'ktm','200 rc':'ktm',
    'rc 390':'ktm','rc390':'ktm','390 rc':'ktm',
    'adventure 250':'ktm','250 adventure':'ktm',
    'adventure 390':'ktm','390 adventure':'ktm',
    'adventure 790':'ktm','adventure 890':'ktm',
    'adventure 1090':'ktm','adventure 1190':'ktm',
    '1290 super adventure':'ktm','1290 super adventure s':'ktm',
    '390 smr':'ktm','390 enduro r':'ktm',
    'freeride 250r':'ktm','freeride e-xc':'ktm',
    '450 exc-f':'ktm','300 exc':'ktm','150 exc':'ktm',

    # ════════════════════════════════════════════════════════════════
    #  KAWASAKI  (complete)
    # ════════════════════════════════════════════════════════════════
    'ninja 300':'kawasaki','ninja 400':'kawasaki',
    'ninja 650':'kawasaki','ninja 1000':'kawasaki',
    'ninja 1000sx':'kawasaki','ninja h2':'kawasaki',
    'ninja h2r':'kawasaki','ninja h2 sx':'kawasaki',
    'ninja zx-6r':'kawasaki','zx-6r':'kawasaki',
    'ninja zx-10r':'kawasaki','zx-10r':'kawasaki',
    'ninja zx-14r':'kawasaki','zx-14r':'kawasaki',
    'ninja zx-25r':'kawasaki','zx-25r':'kawasaki',
    'ninja zx4r':'kawasaki','ninja zx4rr':'kawasaki',
    'z300':'kawasaki','z400':'kawasaki','z650':'kawasaki',
    'z800':'kawasaki','z900':'kawasaki',
    'z1000':'kawasaki','z1000sx':'kawasaki',
    'versys 300':'kawasaki','versys 300x':'kawasaki',
    'versys 650':'kawasaki','versys 1000':'kawasaki',
    'versys':'kawasaki',
    'w800':'kawasaki','w800 cafe':'kawasaki',
    'er-6n':'kawasaki','er-6f':'kawasaki',
    'eliminator 500':'kawasaki','eliminator':'kawasaki',
    'vulcan s':'kawasaki','vulcan 900':'kawasaki',
    'klr 650':'kawasaki',
    'h2 carbon':'kawasaki',

    # ════════════════════════════════════════════════════════════════
    #  SUZUKI BIKES  (complete)
    # ════════════════════════════════════════════════════════════════
    'samurai':'suzuki','shogun':'suzuki','max 100 suzuki':'suzuki',
    'saber':'suzuki','sprinter':'suzuki','zeus':'suzuki',
    'gixxer':'suzuki','gixxer sf':'suzuki',
    'gixxer 250':'suzuki','gixxer sf 250':'suzuki',
    'gixxer sf moto gp':'suzuki',
    'hayabusa':'suzuki','hayabusa 2021':'suzuki',
    'v-strom 650':'suzuki','v-strom 650 xt':'suzuki',
    'v-strom 1050':'suzuki','v-strom 1050 xt':'suzuki',
    'v-strom':'suzuki',
    'katana':'suzuki',
    'gsx-r150':'suzuki','gsx-r600':'suzuki',
    'gsx-r750':'suzuki','gsx-r1000':'suzuki',
    'gsx-s750':'suzuki','gsx-s1000':'suzuki',
    'intruder 150':'suzuki','intruder m1800r':'suzuki',
    'intruder':'suzuki',
    'sv650':'suzuki','sv1000':'suzuki',
    'bandit 650':'suzuki','bandit 1250':'suzuki',
    'dl650':'suzuki','dl1000':'suzuki','dl1050':'suzuki',
    # Scooters
    'access 125':'suzuki','access':'suzuki',
    'burgman 125':'suzuki','burgman street':'suzuki','burgman':'suzuki',
    'avenis 125':'suzuki','avenis':'suzuki',
    'swish 125':'suzuki','swish':'suzuki','lets':'suzuki',

    # ════════════════════════════════════════════════════════════════
    #  TRIUMPH  (complete)
    # ════════════════════════════════════════════════════════════════
    'speed 400':'triumph','scrambler 400x':'triumph',
    'scrambler 400':'triumph',
    'street triple 660':'triumph','street triple r':'triumph',
    'street triple rs':'triumph','street triple':'triumph',
    'trident 660':'triumph','trident':'triumph',
    'daytona 660':'triumph','daytona 675':'triumph',
    'daytona moto2 765':'triumph',
    'tiger sport 660':'triumph','tiger sport 800':'triumph',
    'tiger 900':'triumph','tiger 900 gt':'triumph',
    'tiger 900 rally':'triumph',
    'tiger 1200':'triumph','tiger 1200 gt':'triumph',
    'tiger 1200 rally':'triumph',
    'tiger 850 sport':'triumph',
    'bonneville t100':'triumph','bonneville t120':'triumph',
    'bonneville':'triumph',
    'street scrambler':'triumph','desert sled':'triumph',
    'thruxton 1200':'triumph','thruxton r':'triumph','thruxton':'triumph',
    'rocket 3 r':'triumph','rocket 3 gt':'triumph','rocket 3':'triumph',
    'speedmaster 1200':'triumph','speedmaster':'triumph',
    'speed twin 900':'triumph','speed twin 1200':'triumph',
    'america':'triumph',

    # ════════════════════════════════════════════════════════════════
    #  JAWA / YEZDI
    # ════════════════════════════════════════════════════════════════
    'jawa 42':'jawa','jawa 42 bobber':'jawa',
    'jawa classic':'jawa','jawa perak':'jawa',
    'jawa 350':'jawa','jawa 42 fj':'jawa',
    'jawa 300 ohc':'jawa','jawa 350 classic':'jawa',
    'perak':'jawa',
    'roadster':'yezdi','yezdi roadster':'yezdi',
    'yezdi scrambler':'yezdi','scrambler yezdi':'yezdi',
    'yezdi adventure':'yezdi','adventure yezdi':'yezdi',

    # ════════════════════════════════════════════════════════════════
    #  HARLEY DAVIDSON  (complete)
    # ════════════════════════════════════════════════════════════════
    'x440':'harley davidson','x440 s':'harley davidson',
    'x440 vivid':'harley davidson',
    'street 500':'harley davidson','street 750':'harley davidson',
    'street rod':'harley davidson',
    'iron 883':'harley davidson','iron 1200':'harley davidson',
    'forty-eight':'harley davidson','forty eight special':'harley davidson',
    'sportster s':'harley davidson','nightster':'harley davidson',
    'fat bob 114':'harley davidson','fat bob 114 s':'harley davidson',
    'fat bob':'harley davidson',
    'fat boy 114':'harley davidson','fat boy 117':'harley davidson',
    'fat boy':'harley davidson',
    'softail slim':'harley davidson','softail standard':'harley davidson',
    'low rider s':'harley davidson','low rider el diablo':'harley davidson',
    'low rider':'harley davidson',
    'heritage classic 114':'harley davidson',
    'heritage classic':'harley davidson',
    'breakout 114':'harley davidson','breakout 117':'harley davidson',
    'breakout':'harley davidson',
    'street glide special':'harley davidson',
    'street glide st':'harley davidson','street glide':'harley davidson',
    'road glide special':'harley davidson',
    'road glide limited':'harley davidson','road glide':'harley davidson',
    'road king special':'harley davidson','road king':'harley davidson',
    'ultra limited':'harley davidson',
    'cvo street glide':'harley davidson','cvo limited':'harley davidson',
    'electra glide':'harley davidson','electra glide ultra':'harley davidson',
    'tri glide ultra':'harley davidson','freewheeler':'harley davidson',
    'pan america 1250':'harley davidson','pan america':'harley davidson',
    'livewire one':'harley davidson','livewire':'harley davidson',

    # ════════════════════════════════════════════════════════════════
    #  DUCATI  (complete)
    # ════════════════════════════════════════════════════════════════
    'panigale v2':'ducati','panigale v4':'ducati',
    'panigale v4 s':'ducati','panigale v4 r':'ducati',
    '899 panigale':'ducati','959 panigale':'ducati',
    '1199 panigale':'ducati','1299 panigale':'ducati',
    'panigale':'ducati',
    'monster plus':'ducati','monster 821':'ducati',
    'monster 1200s':'ducati','monster 1200':'ducati',
    'monster':'ducati',
    'multistrada v4':'ducati','multistrada v4 s':'ducati',
    'multistrada 950':'ducati','multistrada 1260':'ducati',
    'multistrada':'ducati',
    'scrambler icon':'ducati','scrambler sixty2':'ducati',
    'scrambler full throttle':'ducati',
    'scrambler urban motard':'ducati',
    'scrambler ducati':'ducati','scrambler':'ducati',
    'diavel v4':'ducati','diavel 1260 s':'ducati',
    'diavel 1260':'ducati','diavel':'ducati',
    'xdiavel s':'ducati','xdiavel darko':'ducati','xdiavel':'ducati',
    'streetfighter v4':'ducati','streetfighter v2':'ducati',
    'streetfighter v4 s':'ducati','streetfighter':'ducati',
    'hypermotard 950':'ducati','hypermotard':'ducati',
    'supersport 950':'ducati','supersport 950s':'ducati',
    'supersport':'ducati',
    'desert sled ducati':'ducati',

    # ════════════════════════════════════════════════════════════════
    #  BMW MOTORRAD  (complete)
    # ════════════════════════════════════════════════════════════════
    'g310r':'bmw motorrad','g 310 r':'bmw motorrad',
    'g310gs':'bmw motorrad','g 310 gs':'bmw motorrad',
    'g310rr':'bmw motorrad','g 310 rr':'bmw motorrad',
    'f750gs':'bmw motorrad','f 750 gs':'bmw motorrad',
    'f850gs':'bmw motorrad','f 850 gs':'bmw motorrad',
    'f850gs adventure':'bmw motorrad',
    'f900r':'bmw motorrad','f 900 r':'bmw motorrad',
    'f900xr':'bmw motorrad','f 900 xr':'bmw motorrad',
    'r1250gs':'bmw motorrad','r 1250 gs':'bmw motorrad',
    'r1250gs adventure':'bmw motorrad',
    'r1250rt':'bmw motorrad','r 1250 rt':'bmw motorrad',
    'r1250r':'bmw motorrad','r 1250 r':'bmw motorrad',
    's1000rr':'bmw motorrad','s 1000 rr':'bmw motorrad',
    's1000r':'bmw motorrad','s 1000 r':'bmw motorrad',
    's1000xr':'bmw motorrad','s 1000 xr':'bmw motorrad',
    'm1000rr':'bmw motorrad','m 1000 rr':'bmw motorrad',
    'm1000r':'bmw motorrad','m 1000 r':'bmw motorrad',
    'r ninet':'bmw motorrad','r nine t':'bmw motorrad',
    'r ninet scrambler':'bmw motorrad',
    'r ninet racer':'bmw motorrad',
    'r ninet urban gs':'bmw motorrad',
    'r18':'bmw motorrad','r 18':'bmw motorrad',
    'r18 classic':'bmw motorrad','r18 transcontinental':'bmw motorrad',
    'k1600gt':'bmw motorrad','k 1600 gt':'bmw motorrad',
    'k1600gtl':'bmw motorrad','k 1600 gtl':'bmw motorrad',
    'ce 02':'bmw motorrad','ce 04':'bmw motorrad',

    # ════════════════════════════════════════════════════════════════
    #  CFMOTO  (complete)
    # ════════════════════════════════════════════════════════════════
    '150nk':'cfmoto','300nk':'cfmoto','400nk':'cfmoto',
    '650nk':'cfmoto','650gt':'cfmoto','650mt':'cfmoto',
    '800mt':'cfmoto','800mt adventure':'cfmoto',
    '1250tr-g':'cfmoto','700cl-x':'cfmoto',
    '250sr':'cfmoto','300ss':'cfmoto','450sr':'cfmoto','450mt':'cfmoto',
    'cfmoto 300nk':'cfmoto','cfmoto 650nk':'cfmoto',
    'cfmoto 650mt':'cfmoto',

    # ════════════════════════════════════════════════════════════════
    #  BENELLI  (complete)
    # ════════════════════════════════════════════════════════════════
    'tnt 150':'benelli','tnt 150s':'benelli','tnt 25':'benelli',
    'tnt 300':'benelli','tnt 302r':'benelli','tnt 302s':'benelli',
    'tnt 600':'benelli','tnt 899':'benelli',
    '302r':'benelli','bn 600':'benelli','752s':'benelli',
    '1200gt':'benelli','leoncino 250':'benelli',
    'leoncino 500':'benelli','leoncino':'benelli',
    'trk 502':'benelli','trk 502x':'benelli','trk 800x':'benelli',
    'imperiale 400':'benelli',

    # ════════════════════════════════════════════════════════════════
    #  HUSQVARNA
    # ════════════════════════════════════════════════════════════════
    'svartpilen 250':'husqvarna','svartpilen 401':'husqvarna',
    'svartpilen 125':'husqvarna','svartpilen':'husqvarna',
    'vitpilen 250':'husqvarna','vitpilen 401':'husqvarna',
    'vitpilen 125':'husqvarna','vitpilen':'husqvarna',

    # ════════════════════════════════════════════════════════════════
    #  APRILIA
    # ════════════════════════════════════════════════════════════════
    'sr 125':'aprilia','sr 160':'aprilia','sr 200':'aprilia',
    'storm 125':'aprilia',
    'rsv4':'aprilia','rsv4 r':'aprilia','rsv4 factory':'aprilia',
    'rs 660':'aprilia','rs 660 trofeo':'aprilia',
    'tuono 660':'aprilia','tuono v4':'aprilia','tuono factory':'aprilia',
    'shiver 750':'aprilia','dorsoduro 750':'aprilia',
    'rx 125':'aprilia','sx 125':'aprilia',

    # ════════════════════════════════════════════════════════════════
    #  VESPA
    # ════════════════════════════════════════════════════════════════
    'vxl 125':'vespa','vxl 150':'vespa',
    'sxl 125':'vespa','sxl 150':'vespa',
    'zx 125':'vespa','vespa zx 125':'vespa',
    'elegante 150':'vespa','vespa 946':'vespa',
    'primavera 125':'vespa','sprint 125':'vespa',
    'gts 300':'vespa','gts super':'vespa',
    'lx 125':'vespa','lx 150':'vespa',

    # ════════════════════════════════════════════════════════════════
    #  OLA ELECTRIC
    # ════════════════════════════════════════════════════════════════
    'ola s1 pro':'ola','ola s1 air':'ola','ola s1 x':'ola',
    'ola s1':'ola','s1 pro':'ola','s1 air':'ola','s1 x':'ola',
    's1 x+':'ola','s1 pro gen2':'ola',
    'roadster x':'ola','roadster pro':'ola',
    'roadster ultra':'ola','ola roadster':'ola',

    # ════════════════════════════════════════════════════════════════
    #  ATHER ENERGY
    # ════════════════════════════════════════════════════════════════
    'ather 450x':'ather','ather 450s':'ather',
    'ather rizta':'ather','ather rizta z':'ather',
    'ather 450 apex':'ather','450x':'ather','450s':'ather',
    'rizta':'ather','ather 340':'ather',

    # ════════════════════════════════════════════════════════════════
    #  REVOLT / ULTRAVIOLETTE / MATTER
    # ════════════════════════════════════════════════════════════════
    'rv400':'revolt','rv1':'revolt','rv400 bf':'revolt',
    'f77':'ultraviolette','f77 mach 2':'ultraviolette',
    'matter aera':'matter','aera 5000':'matter',

    # ════════════════════════════════════════════════════════════════
    #  ELECTRIC SCOOTERS (other brands)
    # ════════════════════════════════════════════════════════════════
    'magnus':'ampere','magnus ex':'ampere','primus':'ampere',
    'zeal':'ampere','ampere magnus':'ampere',
    'ridge plus':'okinawa','r30':'okinawa','lite':'okinawa',
    'optima plus':'okinawa','praise pro':'okinawa',
    'flash':'okinawa','okinawa ridge':'okinawa',
    'photon':'hero electric','optima cx':'hero electric',
    'flash e5':'hero electric','nyx er':'hero electric',
    'one':'simple energy','simple one':'simple energy',
    'bounce infinity e1':'bounce infinity',
    'kabira km3000':'kabira','kabira km4000':'kabira',
    'bgauss b8':'bgauss','bgauss a2':'bgauss','bgauss c8':'bgauss',

    # ════════════════════════════════════════════════════════════════
    #  ASHOK LEYLAND COMMERCIAL  (complete)
    # ════════════════════════════════════════════════════════════════
    'dost':'ashok leyland','dost plus':'ashok leyland',
    'dost strong':'ashok leyland','dost cng':'ashok leyland',
    'dost ev':'ashok leyland',
    'partner':'ashok leyland','partner 4 tyre':'ashok leyland',
    'bada dost i cng':'ashok leyland','bada dost':'ashok leyland',
    'ecomet 1215':'ashok leyland','ecomet 1415':'ashok leyland',
    '1616il':'ashok leyland','2516il':'ashok leyland',
    '2816il':'ashok leyland','3516il':'ashok leyland',
    '4923il':'ashok leyland','5523il':'ashok leyland',
    'u 3518':'ashok leyland','u 4923':'ashok leyland',
    'captain 2516':'ashok leyland','captain 3516':'ashok leyland',
    'boss 1616':'ashok leyland','boss 2518':'ashok leyland',
    'stile':'ashok leyland',
    'viking':'ashok leyland','cheetah':'ashok leyland',
    'janbus':'ashok leyland','sunshine':'ashok leyland',
    'falcon bus':'ashok leyland','hybus':'ashok leyland',
    'circuit bus':'ashok leyland','e-circuit':'ashok leyland',
    '222 bus':'ashok leyland','252 bus':'ashok leyland',
    'skyline bus':'ashok leyland',

    # ════════════════════════════════════════════════════════════════
    #  EICHER COMMERCIAL  (complete)
    # ════════════════════════════════════════════════════════════════
    'pro 1049':'eicher','pro 1059':'eicher','pro 1075':'eicher',
    'pro 1110':'eicher','pro 1114':'eicher','pro 1114xp':'eicher',
    'pro 2049':'eicher','pro 2059':'eicher','pro 2075':'eicher',
    'pro 2095':'eicher',
    'pro 3008':'eicher','pro 3009':'eicher','pro 3010':'eicher',
    'pro 3014':'eicher','pro 3015':'eicher',
    'pro 6016':'eicher','pro 6025':'eicher','pro 6031':'eicher',
    'skyline pro bus':'eicher','starline bus':'eicher',
    'e 475':'eicher','e 483':'eicher',

    # ════════════════════════════════════════════════════════════════
    #  BHARAT BENZ
    # ════════════════════════════════════════════════════════════════
    '914r':'bharat benz','1015r':'bharat benz',
    '1217r':'bharat benz','1617r':'bharat benz',
    '2523r':'bharat benz','2528r':'bharat benz',
    '3128r':'bharat benz','3531r':'bharat benz',
    '4228r':'bharat benz','4240r':'bharat benz',
    'sfc 814':'bharat benz','fmx 42r':'bharat benz',

    # ════════════════════════════════════════════════════════════════
    #  FORCE MOTORS
    # ════════════════════════════════════════════════════════════════
    'gurkha':'force','force gurkha':'force',
    'force trax':'force','trax toofan':'force',
    'force one':'force','force kargo king':'force',
    'trump 26':'force','trump 40':'force',
    'traveller 12':'force','traveller 13':'force',
    'traveller 14':'force','traveller 17':'force',
    'traveller 20':'force','urbania':'force',
    'cruiser 17':'force','wagoneer force':'force',

    # ════════════════════════════════════════════════════════════════
    #  PIAGGIO
    # ════════════════════════════════════════════════════════════════
    'ape city plus':'piaggio','ape xtra ldx':'piaggio',
    'ape hd':'piaggio','ape truk plus':'piaggio',
    'ape auto':'piaggio','ape e-city':'piaggio',
    'ape e-xtra':'piaggio','ape':'piaggio',

    # ════════════════════════════════════════════════════════════════
    #  JOHN DEERE TRACTORS  (complete)
    # ════════════════════════════════════════════════════════════════
    '3028 en':'john deere','3036 en':'john deere','3038 el':'john deere',
    '5042d':'john deere','5045d':'john deere','5048d':'john deere',
    '5050d':'john deere','5050e':'john deere','5055d':'john deere',
    '5060d':'john deere','5065e':'john deere','5075e':'john deere',
    '5090e':'john deere','5105':'john deere','5310':'john deere',
    '5310s':'john deere','5405':'john deere','5405 gearPro':'john deere',
    '5415':'john deere','5503':'john deere',
    '5615':'john deere','5705':'john deere',
    '6110b':'john deere','6120b':'john deere',
    'e series 5050':'john deere','b series 5042':'john deere',

    # ════════════════════════════════════════════════════════════════
    #  SWARAJ TRACTORS  (complete)
    # ════════════════════════════════════════════════════════════════
    'swaraj 717 fe':'swaraj','swaraj 722 fe':'swaraj',
    'swaraj 724 fe':'swaraj','swaraj 735 fe':'swaraj',
    'swaraj 742 fe':'swaraj','swaraj 744 fe':'swaraj',
    'swaraj 744 xt':'swaraj','swaraj 745 fe':'swaraj',
    'swaraj 855 fe':'swaraj','swaraj 960 fe':'swaraj',
    'swaraj 963 fe':'swaraj','swaraj 969 fe':'swaraj',
    'swaraj 978 fe':'swaraj',
    '717 fe':'swaraj','722 fe':'swaraj','724 fe':'swaraj',
    '735 fe':'swaraj','744 xt':'swaraj','855 fe':'swaraj',
    '963 fe':'swaraj','969 fe':'swaraj',
    'excel 65 swaraj':'swaraj','code 65 swaraj':'swaraj',

    # ════════════════════════════════════════════════════════════════
    #  SONALIKA TRACTORS  (complete)
    # ════════════════════════════════════════════════════════════════
    'sonalika di 35':'sonalika','sonalika di 42':'sonalika',
    'sonalika di 745':'sonalika','sonalika tiger 55':'sonalika',
    'sonalika rx 50':'sonalika','sonalika worldtrac 60':'sonalika',
    'dl 35 maharaja':'sonalika','dl 40 maharaja':'sonalika',
    'dl 42 sikandar':'sonalika','dl 45 rx':'sonalika',
    'di 35':'sonalika','di 42':'sonalika','di 42 rx':'sonalika',
    'di 47 rx':'sonalika','di 50 rx':'sonalika',
    'di 60':'sonalika','di 60 rx':'sonalika','di 745 iii':'sonalika',
    'gt 20':'sonalika','gt 22':'sonalika','gt 26':'sonalika',
    'tiger 55':'sonalika','tiger 60':'sonalika','tiger 65':'sonalika',
    'international 90':'sonalika','worldtrac 60':'sonalika',
    'worldtrac 75':'sonalika','sikandar rx 50':'sonalika',
    'sikandar super':'sonalika',

    # ════════════════════════════════════════════════════════════════
    #  NEW HOLLAND TRACTORS  (complete)
    # ════════════════════════════════════════════════════════════════
    'tt 45s':'new holland','tt 45':'new holland',
    'tt 50':'new holland','tt 55':'new holland',
    'tt 75':'new holland','tt 85':'new holland','tt 110':'new holland',
    '3600-2':'new holland','3600 all rounder':'new holland',
    '3630 tx special':'new holland','3630 tx plus':'new holland',
    '4710 specialty':'new holland','5500 turbo super':'new holland',
    'excel 4710':'new holland','excel 5510':'new holland',
    'im 4820':'new holland',
    'td80d':'new holland','td90d':'new holland','td95d':'new holland',
    'ts100a':'new holland','ts110a':'new holland','ts115a':'new holland',
    't5.95':'new holland','t6.165':'new holland',
    'simba nh':'new holland',

    # ════════════════════════════════════════════════════════════════
    #  KUBOTA TRACTORS  (complete)
    # ════════════════════════════════════════════════════════════════
    'b2420':'kubota','b2441':'kubota','b2741':'kubota',
    'l3408':'kubota','l3608':'kubota','l4508':'kubota',
    'l4508 4wd':'kubota','l4018':'kubota','l5018':'kubota',
    'mv1':'kubota','mv2':'kubota','mv3':'kubota',
    'mu4501':'kubota','mu5502':'kubota',
    'neo star a211n':'kubota','neo star a211':'kubota',
    '4508 4wd':'kubota',

    # ════════════════════════════════════════════════════════════════
    #  POWERTRAC TRACTORS  (complete)
    # ════════════════════════════════════════════════════════════════
    'euro 39':'powertrac','euro 41':'powertrac',
    'euro 42':'powertrac','euro 45':'powertrac',
    'euro 47':'powertrac','euro 50':'powertrac',
    'euro 55':'powertrac','euro 60':'powertrac',
    'euro 65':'powertrac','euro 75':'powertrac',
    'alt 3500':'powertrac','alt 4000':'powertrac',
    'plt 120':'powertrac','powertrac 434':'powertrac',
    'powertrac 445':'powertrac','powertrac 455':'powertrac',
    'powertrac 461':'powertrac',

    # ════════════════════════════════════════════════════════════════
    #  MASSEY FERGUSON TRACTORS  (complete)
    # ════════════════════════════════════════════════════════════════
    'mf 241':'massey ferguson','mf 244':'massey ferguson',
    'mf 245':'massey ferguson','mf 246':'massey ferguson',
    'mf 1030':'massey ferguson','mf 1035':'massey ferguson',
    'mf 1042':'massey ferguson','mf 1055':'massey ferguson',
    'mf 5245':'massey ferguson','mf 7250':'massey ferguson',
    'mf 8560':'massey ferguson','mf 9500':'massey ferguson',
    'mf 9500 smart':'massey ferguson',
    'massey 241':'massey ferguson','massey 244':'massey ferguson',
    'massey 1035':'massey ferguson',
    '241 di':'massey ferguson','244 di':'massey ferguson',
    '245 di':'massey ferguson',

    # ════════════════════════════════════════════════════════════════
    #  FARMTRAC TRACTORS
    # ════════════════════════════════════════════════════════════════
    'atom 26':'farmtrac','atom 34':'farmtrac',
    'farmtrac 45':'farmtrac','farmtrac 50':'farmtrac',
    'farmtrac 60':'farmtrac','farmtrac 6055':'farmtrac',
    'farmtrac 6060':'farmtrac','farmtrac 6065':'farmtrac',
    'farmtrac 6075':'farmtrac','farmtrac 80':'farmtrac',
    'champion 37':'farmtrac',

    # ════════════════════════════════════════════════════════════════
    #  ESCORTS TRACTORS
    # ════════════════════════════════════════════════════════════════
    'powertrac 4455':'escorts','steeltrac 26':'escorts',
    'digger 50':'escorts','digger 60':'escorts',

    # ════════════════════════════════════════════════════════════════
    #  HMT TRACTORS
    # ════════════════════════════════════════════════════════════════
    'hmt 2522':'hmt','hmt 2522 dx':'hmt','hmt 3522':'hmt',
    'hmt 4522':'hmt','hmt 5922':'hmt','hmt 6522':'hmt',

    # ════════════════════════════════════════════════════════════════
    #  VST TRACTORS
    # ════════════════════════════════════════════════════════════════
    'shakti mt 171':'vst','shakti mt 180':'vst',
    'shakti mt 224':'vst','shakti mt 270':'vst',
    'field master 430':'vst',

    # ════════════════════════════════════════════════════════════════
    #  INDO FARM TRACTORS
    # ════════════════════════════════════════════════════════════════
    'indo farm 1026':'indo farm','indo farm 2030':'indo farm',
    'indo farm 3035':'indo farm','indo farm 3040':'indo farm',
    '1026 di':'indo farm','2030 di':'indo farm','3035 di':'indo farm',

    # ════════════════════════════════════════════════════════════════
    #  EICHER TRACTOR
    # ════════════════════════════════════════════════════════════════
    'eicher 380':'eicher tractor','eicher 548':'eicher tractor',
    'eicher 557':'eicher tractor','eicher prima g3':'eicher tractor',

    # ════════════════════════════════════════════════════════════════
    #  ACE TRACTORS
    # ════════════════════════════════════════════════════════════════
    'ace di 450':'ace','ace di 550':'ace',
    'dlx 450':'ace','dlx 550':'ace',
}

def _find_model_brand(model_input):
    """Returns correct brand for a model, or None. Longer keys checked first."""
    ml = model_input.lower().strip()
    if not ml:
        return None
    if ml in MODEL_BELONGS_TO:
        return MODEL_BELONGS_TO[ml]
    for key in sorted(MODEL_BELONGS_TO.keys(), key=len, reverse=True):
        if key in ml:
            return MODEL_BELONGS_TO[key]
    return None


def _validate_inputs(vehicle_type, brand, year, condition, km_driven, model):
    vtype = (vehicle_type or '').lower().strip()
    if vtype not in {'cars','bikes','scooters','trucks','tractors'}:
        return "Please select a valid vehicle type."

    if not brand or not brand.strip():
        return "Brand is required."

    bl = brand.lower().strip()
    if bl in BRAND_CORRECTIONS:
        return f'"{brand}" is not recognised. Did you mean "{BRAND_CORRECTIONS[bl]}"?'

    matched_brand = None
    if bl in KNOWN_VEHICLE_BRANDS:
        matched_brand = bl
    else:
        for known in KNOWN_VEHICLE_BRANDS:
            if known in bl or bl in known:
                matched_brand = known; break

    if matched_brand is None:
        close = difflib.get_close_matches(bl, KNOWN_VEHICLE_BRANDS, n=1, cutoff=0.72)
        if close:
            return f'"{brand}" is not a recognised brand. Did you mean "{close[0].title()}"?'
        return (
            f'"{brand}" is not a recognised vehicle brand. '
            f'Please enter a valid manufacturer name '
            f'(e.g. Maruti, Honda, Bajaj, Royal Enfield, Toyota, Tata).'
        )

    allowed_types = BRAND_VEHICLE_TYPES.get(matched_brand, set())
    if allowed_types and vtype not in allowed_types:
        allowed_labels = ' or '.join(TYPE_LABELS[t] for t in sorted(allowed_types))
        selected_label = TYPE_LABELS.get(vtype, vtype.title())
        return (
            f'"{brand.title()}" does not manufacture {selected_label}s. '
            f'{brand.title()} makes {allowed_labels}. '
            f'Please change Vehicle Type to "{allowed_labels}".'
        )

    ml = (model or '').lower().strip()
    if ml:
        correct_brand = _find_model_brand(ml)
        if correct_brand and correct_brand != matched_brand:
            return (
                f'"{model.title()}" is a {correct_brand.title()} model, not {brand.title()}. '
                f'Please change Brand to "{correct_brand.title()}", '
                f'or enter a correct {brand.title()} model name.'
            )

    try:
        yr = int(year)
    except (TypeError, ValueError):
        return "Please enter a valid year (e.g. 2019)."
    if yr < 1980: return "Year cannot be before 1980."
    if yr > CURRENT_YEAR: return f"Year cannot be in the future. Maximum is {CURRENT_YEAR}."

    if not condition or condition.lower() not in {'new','like_new','good','fair','poor'}:
        return "Please select a valid vehicle condition."

    if km_driven is not None:
        try: km = int(km_driven)
        except (TypeError, ValueError): return "KM driven must be a number."
        if km < 0: return "KM driven cannot be negative."
        if km > 2000000: return "KM driven value is unrealistic (max 20,00,000 km)."
        age = CURRENT_YEAR - yr
        if condition == 'new' and km > 500:
            return (f"A 'Brand New' vehicle cannot have {km:,} km driven. "
                    "Set KM to 0 or change condition.")
        if age > 15 and condition == 'like_new':
            return (f"A {yr} vehicle ({age} years old) cannot be 'Like New'. "
                    "Please select Good, Fair, or Poor.")
        if age == 0 and condition in ('fair','poor'):
            return f"A brand new {yr} vehicle cannot be in '{condition.title()}' condition."

    return None


# ── HEURISTIC FALLBACK ─────────────────────────────────────────────────
_BRAND_BASE = {
    'cars':{
        'maruti':820000,'suzuki':820000,'hyundai':1150000,'tata':1050000,
        'honda':1350000,'toyota':2100000,'mahindra':1600000,'kia':1550000,
        'volkswagen':1700000,'skoda':1750000,'renault':830000,'nissan':950000,
        'mg':1900000,'jeep':3600000,'citroen':1000000,'ford':1100000,
        'chevrolet':900000,'fiat':850000,'datsun':650000,'mitsubishi':1400000,
        'opel':850000,'mini':3500000,
        'bmw':7000000,'mercedes':8500000,'audi':6500000,'volvo':6500000,
        'land rover':16000000,'jaguar':10000000,'lexus':11000000,'porsche':15000000,
        'bentley':25000000,'rolls royce':40000000,'ferrari':35000000,
        'lamborghini':35000000,'maserati':12000000,'aston martin':20000000,
        'default':1050000},
    'bikes':{
        'hero':88000,'bajaj':115000,'honda':125000,'tvs':105000,'yamaha':145000,
        'suzuki':140000,'royal enfield':245000,'ktm':310000,'kawasaki':580000,
        'jawa':200000,'triumph':275000,'ducati':1500000,'benelli':350000,
        'cfmoto':400000,'husqvarna':310000,'yezdi':185000,
        'harley davidson':500000,'bmw motorrad':400000,
        'indian':1200000,'norton':800000,'ultraviolette':350000,'matter':300000,
        'revolt':150000,'default':115000},
    'scooters':{
        'honda':92000,'tvs':92000,'hero':82000,'suzuki':98000,'yamaha':92000,
        'ola':138000,'ather':168000,'bajaj':135000,'vespa':140000,
        'aprilia':115000,'piaggio':95000,'hero electric':85000,
        'okinawa':80000,'ampere':85000,'bgauss':95000,
        'simple energy':140000,'bounce infinity':80000,'default':92000},
    'trucks':{
        'tata':2100000,'ashok leyland':2300000,'mahindra':1900000,
        'eicher':2500000,'force':900000,'bharat benz':3000000,
        'volvo':7000000,'man':5500000,'scania':8000000,
        'isuzu':2800000,'sml isuzu':1800000,'piaggio':400000,
        'default':2100000},
    'tractors':{
        'mahindra':870000,'swaraj':820000,'john deere':1200000,
        'sonalika':880000,'new holland':1050000,'kubota':980000,
        'powertrac':700000,'massey ferguson':900000,'farmtrac':750000,
        'escorts':750000,'kubota':980000,'hmt':650000,'vst':600000,
        'indo farm':720000,'eicher tractor':780000,'default':870000},
}
_DEP = {
    'cars':    [1.00,0.81,0.73,0.67,0.61,0.56,0.52,0.48,0.44,0.41,0.38],
    'bikes':   [1.00,0.82,0.74,0.67,0.61,0.56,0.51,0.47,0.43,0.39,0.36],
    'scooters':[1.00,0.81,0.73,0.65,0.58,0.53,0.48,0.44,0.40,0.37,0.34],
    'trucks':  [1.00,0.84,0.76,0.69,0.63,0.58,0.53,0.49,0.45,0.41,0.38],
    'tractors':[1.00,0.88,0.81,0.74,0.68,0.63,0.59,0.55,0.51,0.48,0.45],
}
_CF={'new':1.00,'like_new':0.97,'good':0.92,'fair':0.80,'poor':0.56}
_FF={'petrol':1.00,'diesel':1.04,'cng':0.90,'electric':0.93,'hybrid':1.06,'lpg':0.87}
_OF={'1':1.00,'2':0.92,'3':0.84,'4':0.75,'5':0.68}
_IF={'comprehensive':1.03,'third_party':1.00,'expired':0.94,'none':0.90}

def _heuristic(vehicle_type,brand,year,condition,km_driven,model,fuel_type,num_owners,insurance):
    vtype=vehicle_type.lower().strip(); bl=brand.lower().strip()
    fl=(fuel_type or 'petrol').lower().strip()
    bmap=_BRAND_BASE.get(vtype,_BRAND_BASE['cars'])
    base=bmap.get('default',1050000)
    for key in bmap:
        if key in bl or bl in key: base=bmap[key]; break
    age=max(0,CURRENT_YEAR-int(year))
    curve=_DEP.get(vtype,_DEP['cars'])
    dep=curve[age] if age<len(curve) else max(0.10,curve[-1]*(0.97**(age-len(curve)+1)))
    km_f=1.0; km=km_driven or 0
    if km>0:
        for lo,hi,f in [(0,15000,1.03),(15001,30000,1.00),(30001,60000,0.93),
                         (60001,90000,0.85),(90001,120000,0.76),(120001,999999,0.62)]:
            if lo<=km<=hi: km_f=f; break
    est=float(base)*dep*_CF.get(condition,0.92)*km_f \
       *_FF.get(fl,1.00)*_OF.get(str(num_owners or '1'),1.00) \
       *_IF.get((insurance or 'third_party').lower(),1.00)
    est=max(5000,round(est/500)*500)
    return {
        'error':None,
        'estimated_price':Decimal(str(int(est))),
        'low_price':Decimal(str(max(5000,round(est*0.88/500)*500))),
        'high_price':Decimal(str(round(est*1.14/500)*500)),
        'explanation':(f"Heuristic estimate for {brand} {model or ''} ({vtype}), "
                       f"{age} yr{'s' if age!=1 else ''} old. "
                       f"AI unavailable — check ANTHROPIC_API_KEY in settings.py."),
        'confidence':'Medium',
        'base_price':Decimal(str(int(base))),
        'age':age,
        'depreciation_pct':round((1-dep)*100,1),
        'resale_tier':'MRV',
    }

_PROMPT="""\
You are an expert Indian automotive resale market analyst. Today is 2025.
Estimate the fair market resale value for this specific vehicle in India.

Vehicle:
  Type     : {vehicle_type}
  Brand    : {brand}
  Model    : {model}
  Year     : {year}  (Age: {age} years)
  Condition: {condition}
  KM Driven: {km_driven}
  Fuel     : {fuel_type}
  Owners   : {num_owners}
  Insurance: {insurance}

Steps:
1. Actual on-road new price for {brand} {model} in {year} India
2. Indian market depreciation (18-20% yr1, 8-12%/yr — Spinny/Cars24 2024)
3. KM vs expected {expected_km} km for {age}-yr-old vehicle
4. Fuel premium/discount (diesel+4%, CNG-8%, EV-7%)
5. Owner premium (1st +8-10% over 2nd)
6. Model demand premium (RE, Activa, Fortuner, Thar etc.)
7. Condition impact

Return ONLY valid JSON:
{{"estimated_price":<int nearest 500>,"low_price":<int nearest 500, 8-12% below>,
"high_price":<int nearest 500, 8-15% above>,"base_new_price":<int on-road new INR>,
"depreciation_pct":<float>,"resale_tier":<"HRV"|"MRV"|"LRV">,
"confidence":<"High"|"Medium"|"Low">,
"explanation":<2-3 sentences on model resale and key factors>}}"""

def _get_api_key():
    key=os.environ.get('ANTHROPIC_API_KEY')
    if key: return key
    try:
        from django.conf import settings
        return getattr(settings,'ANTHROPIC_API_KEY',None)
    except Exception: return None

def _call_claude(prompt):
    client=anthropic.Anthropic(api_key=_get_api_key())
    msg=client.messages.create(model="claude-sonnet-4-6",max_tokens=512,
        messages=[{"role":"user","content":prompt}])
    raw=msg.content[0].text.strip()
    if raw.startswith('```'):
        parts=raw.split('```'); raw=parts[1] if len(parts)>1 else raw
        if raw.startswith('json'): raw=raw[4:]
    return json.loads(raw.strip())

def estimate_price(vehicle_type,brand,year,condition,
                   km_driven=None,model=None,
                   fuel_type='petrol',num_owners='1',
                   insurance='third_party',
                   transmission='manual',color='na'):
    error=_validate_inputs(vehicle_type,brand,year,condition,km_driven,model)
    if error:
        return {'error':error,'estimated_price':None,'low_price':None,
                'high_price':None,'explanation':None,'confidence':None,
                'base_price':None,'age':None,'depreciation_pct':None,'resale_tier':None}

    age=CURRENT_YEAR-int(year)

    if _SDK_OK and _get_api_key():
        try:
            expected_km=age*(12000 if (vehicle_type or '').lower()=='cars' else 8000)
            prompt=_PROMPT.format(
                vehicle_type=(vehicle_type or 'Car').title(),
                brand=brand, model=model or 'Not specified',
                year=year, age=age,
                condition=(condition or 'good').replace('_',' ').title(),
                km_driven=f"{km_driven:,}" if km_driven else 'Not specified',
                expected_km=f"{expected_km:,}",
                fuel_type=(fuel_type or 'Petrol').title(),
                num_owners=num_owners or '1',
                insurance=(insurance or 'third_party').replace('_',' ').title(),
            )
            data=_call_claude(prompt)
            est=int(data['estimated_price']); low=int(data.get('low_price',0))
            high=int(data.get('high_price',0)); base=int(data.get('base_new_price',0))
            if est<=0: raise ValueError("Zero price")
            if low<=0 or low>=est: low=round(est*0.90/500)*500
            if high<=est: high=round(est*1.12/500)*500
            return {
                'error':None,
                'estimated_price':Decimal(str(max(5000,est))),
                'low_price':Decimal(str(max(5000,low))),
                'high_price':Decimal(str(high)),
                'explanation':str(data.get('explanation','')),
                'confidence':str(data.get('confidence','Medium')),
                'base_price':Decimal(str(max(0,base))),
                'age':age,
                'depreciation_pct':float(data.get('depreciation_pct',0)),
                'resale_tier':str(data.get('resale_tier','MRV')).upper(),
            }
        except Exception as exc:
            logger.warning("AI estimator failed (%s). Using heuristic.",exc)

    return _heuristic(vehicle_type,brand,year,condition,
                      km_driven,model,fuel_type,num_owners,insurance)