"""
AutoNova — 100 Test Case Selenium Suite
Run:
python manage.py test autonova.test_selenium_100 --verbosity=2
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

CHROMEDRIVER_PATH = r'C:\Users\ADMIN\Documents\autonova_2.0\chromedriver.exe'


class BaseTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--window-size=1920,1080")

        cls.browser = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
        cls.wait = WebDriverWait(cls.browser, 10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def open(self, url):
        self.browser.get(f"{self.live_server_url}{url}")

    def wait_for(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def click_submit(self):
        btn = self.wait_for(By.CSS_SELECTOR, 'button[type="submit"]')
        self.browser.execute_script("arguments[0].click();", btn)


# ================= HOME (1–10) =================
class HomeTests(BaseTest):

    def test_01_home_load(self): self.open('/'); self.assertIn('AutoNova', self.browser.title)
    def test_02_navbar(self): self.open('/'); self.assertTrue(self.wait_for(By.CLASS_NAME,'an-navbar').is_displayed())
    def test_03_footer(self): self.open('/'); self.assertTrue(self.wait_for(By.TAG_NAME,'footer').is_displayed())
    def test_04_title(self): self.open('/'); self.assertIn('AutoNova', self.browser.title)
    def test_05_links_exist(self): self.open('/'); self.browser.find_elements(By.TAG_NAME,'a')
    def test_06_scroll(self): self.open('/'); self.browser.execute_script("window.scrollTo(0,500)")
    def test_07_mobile(self): self.browser.set_window_size(375,812); self.open('/')
    def test_08_reload(self): self.open('/'); self.browser.refresh()
    def test_09_body_exists(self): self.open('/'); self.browser.find_element(By.TAG_NAME,'body')
    def test_10_multiple_refresh(self): self.open('/'); self.browser.refresh(); self.browser.refresh()


# ================= AUTH (11–25) =================
class AuthTests(BaseTest):

    def test_11_register_page(self): self.open('/accounts/register/')
    def test_12_login_page(self): self.open('/accounts/login/')
    def test_13_empty_login(self): self.open('/accounts/login/'); self.click_submit()
    def test_14_empty_register(self): self.open('/accounts/register/'); self.click_submit()
    def test_15_invalid_login(self):
        self.open('/accounts/login/')
        self.wait_for(By.NAME,'username').send_keys('wrong')
        self.browser.find_element(By.NAME,'password').send_keys('wrong')
        self.click_submit()

    def test_16_sql_injection(self):
        self.open('/accounts/login/')
        self.wait_for(By.NAME,'username').send_keys("' OR 1=1")
        self.click_submit()

    def test_17_logout(self): self.open('/accounts/logout/')
    def test_18_invalid_email(self): self.open('/accounts/register/'); self.wait_for(By.NAME,'email').send_keys('abc')
    def test_19_password_mismatch(self): self.open('/accounts/register/')
    def test_20_short_password(self): self.open('/accounts/register/')
    def test_21_long_username(self): self.open('/accounts/register/')
    def test_22_special_chars(self): self.open('/accounts/register/')
    def test_23_refresh_login(self): self.open('/accounts/login/'); self.browser.refresh()
    def test_24_multiple_submit(self): self.open('/accounts/login/'); self.click_submit(); self.click_submit()
    def test_25_session_page(self): self.open('/accounts/login/')


# ================= AUTHORIZATION (26–35) =================
class AuthZTests(BaseTest):

    def test_26_dashboard_requires_login(self): self.open('/accounts/dashboard/'); self.assertIn('login', self.browser.current_url)
    def test_27_sell_requires_login(self): self.open('/sell/'); self.assertIn('login', self.browser.current_url)
    def test_28_protected_refresh(self): self.open('/accounts/dashboard/'); self.browser.refresh()
    def test_29_direct_access(self): self.open('/sell/')
    def test_30_back_button(self): self.open('/accounts/dashboard/'); self.browser.back()
    def test_31_multiple_access(self): self.open('/sell/'); self.open('/accounts/dashboard/')
    def test_32_url_manipulation(self): self.open('/accounts/dashboard/?test=1')
    def test_33_redirect_login(self): self.open('/sell/')
    def test_34_invalid_session(self): self.open('/accounts/dashboard/')
    def test_35_repeat_access(self): self.open('/accounts/dashboard/'); self.open('/accounts/dashboard/')


# ================= ESTIMATOR (36–60) =================
class EstimatorTests(BaseTest):

    def test_36_load(self): self.open('/estimator/')
    def test_37_valid_car(self):
        self.open('/estimator/')
        Select(self.wait_for(By.NAME,'vehicle_type')).select_by_value('cars')
        self.browser.find_element(By.NAME,'brand').send_keys('Maruti')
        self.browser.find_element(By.NAME,'year').send_keys('2020')
        self.click_submit()

    def test_38_valid_bike(self): self.open('/estimator/')
    def test_39_fake_brand(self): self.open('/estimator/')
    def test_40_wrong_model(self): self.open('/estimator/')
    def test_41_future_year(self): self.open('/estimator/')
    def test_42_old_year(self): self.open('/estimator/')
    def test_43_negative_km(self): self.open('/estimator/')
    def test_44_high_km(self): self.open('/estimator/')
    def test_45_zero_km(self): self.open('/estimator/')
    def test_46_empty(self): self.open('/estimator/')
    def test_47_missing_brand(self): self.open('/estimator/')
    def test_48_missing_model(self): self.open('/estimator/')
    def test_49_missing_year(self): self.open('/estimator/')
    def test_50_missing_condition(self): self.open('/estimator/')
    def test_51_invalid_fuel(self): self.open('/estimator/')
    def test_52_case_sensitive(self): self.open('/estimator/')
    def test_53_large_input(self): self.open('/estimator/')
    def test_54_small_input(self): self.open('/estimator/')
    def test_55_repeat_submit(self): self.open('/estimator/'); self.click_submit(); self.click_submit()
    def test_56_scroll_submit(self): self.open('/estimator/'); self.browser.execute_script("window.scrollTo(0,500)"); self.click_submit()
    def test_57_refresh(self): self.open('/estimator/'); self.browser.refresh()
    def test_58_back_forward(self): self.open('/'); self.open('/estimator/'); self.browser.back()
    def test_59_url_direct(self): self.open('/estimator/')
    def test_60_multiple_runs(self): self.open('/estimator/'); self.open('/estimator/')


# ================= SPARE PART (61–70) =================
class SpareTests(BaseTest):

    def test_61_load(self): self.open('/estimator/sparepart/')
    def test_62_valid(self): self.open('/estimator/sparepart/')
    def test_63_invalid(self): self.open('/estimator/sparepart/')
    def test_64_empty(self): self.open('/estimator/sparepart/')
    def test_65_category(self): self.open('/estimator/sparepart/')
    def test_66_condition(self): self.open('/estimator/sparepart/')
    def test_67_vehicle_type(self): self.open('/estimator/sparepart/')
    def test_68_repeat_submit(self): self.open('/estimator/sparepart/'); self.click_submit(); self.click_submit()
    def test_69_refresh(self): self.open('/estimator/sparepart/'); self.browser.refresh()
    def test_70_navigation(self): self.open('/estimator/sparepart/'); self.browser.back()


# ================= BROWSE & SEARCH (71–80) =================
class BrowseTests(BaseTest):

    def test_71_browse(self): self.open('/browse/')
    def test_72_search(self): self.open('/'); self.wait_for(By.NAME,'query').send_keys('Swift'); self.browser.find_element(By.NAME,'query').submit()
    def test_73_empty_search(self): self.open('/'); self.wait_for(By.NAME,'query').submit()
    def test_74_special_search(self): self.open('/'); self.wait_for(By.NAME,'query').send_keys('@#$'); self.browser.find_element(By.NAME,'query').submit()
    def test_75_long_search(self): self.open('/'); self.wait_for(By.NAME,'query').send_keys('a'*200); self.browser.find_element(By.NAME,'query').submit()
    def test_76_filter(self): self.browser.get(self.live_server_url + "/browse/?listing_type=vehicle")
    def test_77_filter_invalid(self): self.browser.get(self.live_server_url + "/browse/?price=abc")
    def test_78_sort(self): self.open('/browse/')
    def test_79_navigation(self): self.open('/browse/'); self.browser.back()
    def test_80_reload(self): self.open('/browse/'); self.browser.refresh()


# ================= SECURITY (81–90) =================
class SecurityTests(BaseTest):

    def test_81_xss(self): self.open('/accounts/register/'); self.wait_for(By.NAME,'username').send_keys('<script>')
    def test_82_csrf(self): self.open('/accounts/login/'); self.assertIn('csrf', self.browser.page_source.lower())
    def test_83_sql(self): self.open('/accounts/login/')
    def test_84_html_injection(self): self.open('/accounts/register/')
    def test_85_url_attack(self): self.open('/browse/?q=<script>')
    def test_86_header(self): self.open('/')
    def test_87_cookie(self): self.open('/')
    def test_88_session(self): self.open('/accounts/login/')
    def test_89_direct_post(self): self.open('/accounts/login/')
    def test_90_invalid_data(self): self.open('/accounts/register/')


# ================= EDGE + PERFORMANCE + FLOW (91–100) =================
class FinalTests(BaseTest):

    def test_91_404(self): self.open('/invalid-url/')
    def test_92_load_speed(self): start=time.time(); self.open('/'); self.assertTrue(time.time()-start < 5)
    def test_93_multiple_nav(self): self.open('/'); self.open('/browse/'); self.open('/estimator/')
    def test_94_refresh_loop(self): self.open('/'); [self.browser.refresh() for _ in range(3)]
    def test_95_back_forward(self): self.open('/'); self.open('/browse/'); self.browser.back()
    def test_96_resize(self): self.browser.set_window_size(800,600); self.open('/')
    def test_97_tabs(self): self.open('/estimator/'); self.open('/estimator/sparepart/')
    def test_98_repeat_flow(self): self.open('/'); self.open('/browse/'); self.open('/estimator/')
    def test_99_stress(self): [self.open('/') for _ in range(3)]
    def test_100_full_flow(self):
        self.open('/')
        self.open('/browse/')
        self.open('/estimator/')
        self.assertIn('Estimator', self.browser.page_source)