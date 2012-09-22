"""Basic PlantShare functional tests that do not require a browser."""

from django.contrib.auth.models import User
from django.test.client import Client

from selenium.common.exceptions import NoSuchElementException

from gobotany.libtest import FunctionalCase

class PlantShareTests(FunctionalCase):

    TEST_USERNAME = 'test'
    TEST_EMAIL = 'test@test.com'
    TEST_PASSWORD = 'testpass'

    def setUp(self):
        self.user = User.objects.create_user(
            self.TEST_USERNAME, self.TEST_EMAIL, self.TEST_PASSWORD)

    def _get_plantshare(self, url_path, log_in=False):
        client = None
        if log_in:
            client = Client()
            client.login(username=self.TEST_USERNAME,
                         password=self.TEST_PASSWORD)
        PLANTSHARE_BASE = '/ps'
        self.get(PLANTSHARE_BASE + url_path, client=client)

    # PlantShare main page

    MAIN_URL = '/'

    def test_main_page_title(self):
        self._get_plantshare(self.MAIN_URL)
        title = self.css1('title').text
        self.assertEqual(title, 'PlantShare: Go Botany')

    def test_main_page_main_heading(self):
        self._get_plantshare(self.MAIN_URL)
        h1 = self.css1('h1').text
        self.assertEqual(h1, 'PlantShare')

    # PlantShare main page: logged out

    def test_main_page_logged_out_has_signup_nav_link(self):
        self._get_plantshare(self.MAIN_URL)
        self.assertIsNotNone(self.link_saying('Sign Up for PlantShare'))

    def test_main_page_logged_out_has_signup_call_to_action(self):
        self._get_plantshare(self.MAIN_URL)
        self.assertTrue(self.css1('.sign-up-call'))

    def test_main_page_logged_out_has_login_form(self):
        self._get_plantshare(self.MAIN_URL)
        self.assertTrue(self.css1('#login.box'))

    def test_main_page_logged_out_omits_profile_box(self):
        self._get_plantshare(self.MAIN_URL)
        profile_box = None
        try:
            profile_box = self.css1('.profile.box')
        except NoSuchElementException:
            pass
        self.assertIsNone(profile_box)

    def test_main_page_logged_out_omits_profile_nav_link(self):
        self._get_plantshare(self.MAIN_URL)
        link = None
        try:
            link = self.link_saying('My Profile')
        except ValueError:
            pass
        self.assertIsNone(link)

    def test_main_page_logged_out_omits_logout_link(self):
        self._get_plantshare(self.MAIN_URL)
        link = None
        try:
            link = self.link_saying('Log Out')
        except ValueError:
            pass
        self.assertIsNone(link)

    # PlantShare main page: logged in

    def test_main_page_logged_in_has_profile_box(self):
        self._get_plantshare(self.MAIN_URL, log_in=True)
        self.assertTrue(self.css1('.profile.box'))

    def test_main_page_logged_in_has_profile_nav_link(self):
        self._get_plantshare(self.MAIN_URL, log_in=True)
        self.assertIsNotNone(self.link_saying('My Profile'))

    def test_main_page_logged_in_has_logout_link(self):
        self._get_plantshare(self.MAIN_URL, log_in=True)
        self.assertIsNotNone(self.link_saying('Log Out'))

    def test_main_page_logged_in_omits_signup_nav_link(self):
        self._get_plantshare(self.MAIN_URL, log_in=True)
        link = None
        try:
            link = self.link_saying('Sign Up for PlantShare')
        except ValueError:
            pass
        self.assertIsNone(link)

    def test_main_page_logged_in_omits_signup_call_to_action(self):
        self._get_plantshare(self.MAIN_URL, log_in=True)
        call_to_action = None
        try:
            call_to_action = self.css1('.sign-up-call')
        except NoSuchElementException:
            pass
        self.assertIsNone(call_to_action)

    def test_main_page_logged_in_omits_login_form(self):
        self._get_plantshare(self.MAIN_URL, log_in=True)
        form = None
        try:
            form = self.css1('#login.box')
        except NoSuchElementException:
            pass
        self.assertIsNone(form)

    # Sign Up for PlantShare page

    SIGNUP_FORM_URL = '/accounts/register/'

    def test_signup_page_title(self):
        self._get_plantshare(self.SIGNUP_FORM_URL)
        title = self.css1('title').text
        self.assertEqual(title, 'Sign Up for PlantShare: Go Botany')

    def test_signup_page_main_heading(self):
        self._get_plantshare(self.SIGNUP_FORM_URL)
        h1 = self.css1('h1').text
        self.assertEqual(h1, 'Sign Up for PlantShare')

    def test_signup_page_has_plantshare_nav_link(self):
        self._get_plantshare(self.SIGNUP_FORM_URL)
        self.assertIsNotNone(self.link_saying('PlantShare'))

    def test_signup_page_has_minimal_navigation(self):
        self._get_plantshare(self.SIGNUP_FORM_URL)
        navigation_items = self.css('#sidebar .section')
        self.assertEqual(len(navigation_items), 1)

    # My Profile page

    MY_PROFILE_URL = '/profile/'

    def test_profile_page_title(self):
        self._get_plantshare(self.MY_PROFILE_URL)
        title = self.css1('title').text
        self.assertEqual(title, 'My Profile: PlantShare: Go Botany')

    def test_profile_page_main_heading(self):
        self._get_plantshare(self.MY_PROFILE_URL)
        h1 = self.css1('h1').text
        self.assertEqual(h1, 'My Profile')
