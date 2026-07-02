# AutoNova — Vehicle & Spare Parts Marketplace
**Buy & Sell Vehicles and Genuine Spare Parts in India**

---

## 🚀 Quick Setup (PyCharm / Windows)

### 1. Install Requirements
- Python 3.12: https://python.org (check "Add to PATH")
- PyCharm Community: https://jetbrains.com/pycharm/

### 2. Create Project in PyCharm
1. File → New Project
2. Location: `C:\Users\ADMIN\Documents\autonova_final`
3. Virtualenv: New environment using Virtualenv
4. Click **Create**

### 3. Copy Project Files
Extract the zip into your project folder, so the structure is:
```
autonova_final/
├── manage.py
├── requirements.txt
├── seed_data.py
├── autonova/
├── accounts/
├── listings/
├── estimator/
├── templates/
└── static/
```

### 4. Install Dependencies
Open PyCharm Terminal (bottom panel) and run:
```bash
pip install -r requirements.txt
```

### 5. Run Migrations
```bash
python manage.py makemigrations accounts
python manage.py makemigrations listings
python manage.py makemigrations estimator
python manage.py migrate
```

### 6. Create Admin User
```bash
python manage.py createsuperuser
```
Enter: username, email, password when prompted.

### 7. Seed Categories
```bash
python manage.py shell < seed_data.py
```

### 8. Run the Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 📱 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home — browse vehicles & parts |
| `/browse/` | Search & filter all listings |
| `/browse/?listing_type=vehicle` | Vehicles only |
| `/browse/?listing_type=sparepart` | Spare parts only |
| `/sell/` | Choose what to sell |
| `/sell/vehicle/` | List a vehicle |
| `/sell/part/` | List a spare part |
| `/estimator/` | AI price estimator (INR) |
| `/accounts/register/` | Register |
| `/accounts/login/` | Login |
| `/accounts/dashboard/` | Seller dashboard |
| `/admin/` | Admin panel |

---

## 🗂️ Models Overview

### VehicleListing
- Basic: title, brand, model, variant, year, condition
- Vehicle: fuel_type, transmission, km_driven, engine_cc, color
- Legal: rto_state, registration_year, insurance, insurance_valid_until
- Ownership: num_owners, is_negotiable
- Status: pending / approved / rejected / sold

### SparePartListing (separate model, separate fields)
- Part info: part_name, part_number, part_type, brand, condition
- Compatibility: compatible_vehicle_type, compatible_brand, compatible_model, year_from, year_to
- Stock: quantity
- Status: pending / approved / rejected / sold

### Category
- Types: `vehicle` or `sparepart`
- Drives navigation and filtering

---

## 🏷️ Vehicle Categories (seeded)
- 🚗 Cars
- 🚲 Bikes & Scooters
- 🚛 Trucks & Commercial
- 🚜 Tractors & Farm
- 💎 Luxury & Vintage
- ⚡ Electric Vehicles

## ⚙️ Spare Part Categories (seeded)
- Engine Parts
- Body Parts
- Tyres & Wheels
- Batteries & Electrical
- Brakes & Suspension
- Lights & Indicators
- Interior & Accessories
- Filters & Fluids
- Exhaust & Cooling
- Bike Parts

---

## 💰 Price Estimator
Supports: Cars, Bikes, Scooters, Trucks, Tractors
- INR (₹) pricing throughout
- Depreciation by vehicle type
- KM driven adjustment
- Condition multiplier
- Low/High range with confidence

---

## 🔧 Admin Panel Tips
1. Go to `/admin/` and log in
2. **Approve listings**: Listings → Vehicle Listings → change Status to "Approved"
3. **Add categories**: Categories → Add Category (set `category_type`!)
4. **Bulk approve**: Select multiple → Actions → (use list_editable Status column)

---

## 📁 File Structure
```
autonova/          ← Django project settings
accounts/          ← Auth, Profile, Dashboard
listings/          ← VehicleListing, SparePartListing, Categories
estimator/         ← Price engine (INR)
templates/
  base.html        ← Navbar, footer, glow strip
  listings/        ← home, browse, detail, sell, category pages
  accounts/        ← login, register, dashboard, profile
  estimator/       ← estimator page
  partials/        ← vehicle_card.html, part_card.html
static/
  css/autonova.css ← Complete styles + glow strips
  js/autonova.js   ← JS utils
```
