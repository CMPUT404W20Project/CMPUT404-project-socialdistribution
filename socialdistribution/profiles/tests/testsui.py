from profiles.models import Author
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from unittest import skip
from profiles.models import Author
from selenium.webdriver.support.wait import WebDriverWait
import time


class ProfilesUITests(StaticLiveServerTestCase):

    @classmethod
    def create_author(self, uuid_id, email, firstName, lastName, displayName, bio, host, github, password):
        return Author.objects.create(id=uuid_id, email=email, firstName=firstName,lastName=lastName,
                                     displayName=displayName, host=host, github=github, password=password)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_can_signup(self):
        email = "test@gmail.com"
        firstName = "TestFirst"
        lastName = "TestLast"
        password1 = "testPassword"
        password2 = "testPassword"
        displayName = "trial user"
        self.selenium.get('%s%s' % (self.live_server_url, '/register/'))
        firstname_input = self.selenium.find_element_by_name("firstName")
        firstname_input.send_keys(firstName)
        lastName_input = self.selenium.find_element_by_name("lastName")
        lastName_input.send_keys(lastName)
        email_input = self.selenium.find_element_by_name("email")
        email_input.send_keys(email)
        password1_input = self.selenium.find_element_by_name("password1")
        password1_input.send_keys(password1)
        password2_input = self.selenium.find_element_by_name("password2")
        password2_input.send_keys(password2)
        displayName_input = self.selenium.find_element_by_name("displayName")
        displayName_input.send_keys(displayName)
        self.selenium.find_element_by_xpath('//button[@value="Register"]').click()
        redirect = self.selenium.current_url
        self.assertTrue('/accounts/login/' in redirect)

    # User who didn't have a valid account logins
    def test_cannot_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('hi')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('here')
        self.selenium.find_element_by_xpath('//button[@value="Login"]').click()
        # error = self.selenium.find_element_by_class_name("errorlist.nonfield").text
        elem = self.selenium.find_elements_by_css_selector('p')
        error_string = ""
        for el in elem:
            if "Your username and password didn't match." in el.text:
                error_string = el.text

        self.assertEquals("Your username and password didn't match. Please try again.", error_string)

    # User who had a valid account logins
    def test_can_login(self):
        email = "test@gmail.com"
        firstName = "TestFirst"
        lastName = "TestLast"
        password1 = "testPassword"
        password2 = "testPassword"
        displayName = "trial user"
        self.selenium.get('%s%s' % (self.live_server_url, '/register/'))
        firstname_input = self.selenium.find_element_by_name("firstName")
        firstname_input.send_keys(firstName)
        lastName_input = self.selenium.find_element_by_name("lastName")
        lastName_input.send_keys(lastName)
        email_input = self.selenium.find_element_by_name("email")
        email_input.send_keys(email)
        password1_input = self.selenium.find_element_by_name("password1")
        password1_input.send_keys(password1)
        password2_input = self.selenium.find_element_by_name("password2")
        password2_input.send_keys(password2)
        displayName_input = self.selenium.find_element_by_name("displayName")
        displayName_input.send_keys(displayName)
        self.selenium.find_element_by_xpath('//button[@value="Register"]').click()
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(email)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password1)
        self.selenium.find_element_by_xpath('//button[@value="Login"]').click()
        redirect = self.selenium.current_url
        self.assertTrue('/stream/' in redirect)


