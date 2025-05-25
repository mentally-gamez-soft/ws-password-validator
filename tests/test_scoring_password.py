import json
import random

from core.api import ROUTE_PASSWORD_SCORING, ROUTE_WELCOME
from core.service.password_scoring import ColorScore

from . import BaseTestClass


class TestScoringPassword(BaseTestClass):
    def test_welcome_api(self):
        with self.app.app_context():
            response = self.client.get(ROUTE_WELCOME)

            self.assertEqual(200, response.status_code)
            self.assertIn(
                "Welcome to this service for scoring a password.",
                response.get_data(as_text=True),
                "The welcome message is unknowm!",
            )

    def test_scoring_not_allowed_without_api_token(self):
        with self.app.app_context():
            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=self.has_symbols,  # nosec B311
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )
            payload_without_password = {}
            payload_without_password["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload_without_password["min_accepted_score"] = (
                self.characteristics["min_accepted_score"]
            )

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload_without_password,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                401,
                response.status_code,
                "The response status code is unexpected !",
            )
            self.assertEqual(
                "The API key is missing!",
                response_message["message"],
                "The message is not expected !",
            )

    def test_scoring_not_allowed_with_token_used_more_than_max_allowed_calls(
        self,
    ):
        with self.app.app_context():
            user_token = BaseTestClass.get_user().token

            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=self.has_symbols,  # nosec B311
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )
            payload = {}
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]
            for _ in range(1, 30):
                response = self.client.post(
                    ROUTE_PASSWORD_SCORING,
                    json=payload,
                )
            response_message = json.loads(response.text)
            self.assertEqual(
                401,
                response.status_code,
                "The response status code is unexpected !",
            )
            self.assertEqual(
                "The API key limit is reached!",
                response_message["message"],
                "The message is not expected !",
            )

    def test_invalid_payload(self):
        with self.app.app_context():
            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=self.has_symbols,  # nosec B311
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )
            payload_without_password = {}
            user_token = BaseTestClass.get_user().token
            payload_without_password["api_key"] = user_token
            payload_without_password["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload_without_password["min_accepted_score"] = (
                self.characteristics["min_accepted_score"]
            )

            payload_without_characteristics = {}
            user_token = BaseTestClass.get_user().token
            payload_without_characteristics["api_key"] = user_token
            payload_without_characteristics["password"] = password
            payload_without_characteristics["min_accepted_score"] = (
                self.characteristics["min_accepted_score"]
            )

            payload_without_min_valid_scoring = {}
            user_token = BaseTestClass.get_user().token
            payload_without_min_valid_scoring["api_key"] = user_token
            payload_without_min_valid_scoring["password"] = password
            payload_without_min_valid_scoring["characteristics"] = (
                self.characteristics["characteristics"]
            )

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload_without_password,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                400,
                response.status_code,
                "The response status code is unexpected !",
            )
            self.assertEqual(
                "The input data is invalid!",
                response_message["message"],
                "The message is not expected !",
            )
            self.assertEqual(
                "Bad request.",
                response_message["error"],
                "The message is not expected !",
            )

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload_without_characteristics,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                400,
                response.status_code,
                "The response status code is unexpected !",
            )
            self.assertEqual(
                "The input data is invalid!",
                response_message["message"],
                "The message is not expected !",
            )
            self.assertEqual(
                "Bad request.",
                response_message["error"],
                "The message is not expected !",
            )

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload_without_min_valid_scoring,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                400,
                response.status_code,
                "The response status code is unexpected !",
            )
            self.assertEqual(
                "The input data is invalid!",
                response_message["message"],
                "The message is not expected !",
            )
            self.assertEqual(
                "Bad request.",
                response_message["error"],
                "The message is not expected !",
            )

    def test_password_compliant_with_all_requisites(self):
        with self.app.app_context():
            user_token = BaseTestClass.get_user().token
            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=self.has_symbols,  # nosec B311
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )

            payload = {}
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected !",
            )
            self.assertTrue(
                response_message["status"], "The status should be True !"
            )
            self.assertEqual(
                "Your password is valid.",
                response_message["message_password"],
                "The message is not expected !",
            )
            self.assertEqual(
                "Your password is strong enough.",
                response_message["message_score"],
                "The message is not expected !",
            )
            self.assertGreater(
                response_message["score"],
                self.min_accepted_score,
                "The calculated score {} is inferior of the minimal score {}"
                .format(response_message["score"], self.min_accepted_score),
            )

    def test_password_with_minimum_size_compliant_with_all_requisites(self):
        with self.app.app_context():
            user_token = BaseTestClass.get_user().token

            password = self.fake.password(
                length=self.min_length,
                special_chars=self.has_symbols,
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )

            payload = {}
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected !",
            )
            self.assertTrue(
                response_message["status"], "The status should be True !"
            )
            self.assertEqual(
                "Your password is valid.",
                response_message["message_password"],
                "The message is not expected !",
            )
            self.assertEqual(
                "Your password is strong enough.",
                response_message["message_score"],
                "The message is not expected !",
            )
            self.assertGreater(
                response_message["score"],
                self.min_accepted_score,
                "The calculated score {} is inferior of the minimal score {}"
                .format(response_message["score"], self.min_accepted_score),
            )

    def test_password_not_compliant_with_minimum_length(self):
        with self.app.app_context():
            password = self.fake.password(
                length=self.min_length - 1,
                special_chars=self.has_symbols,
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )

            payload = {}
            user_token = BaseTestClass.get_user().token
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected!",
            )
            self.assertFalse(
                response_message["status"], "The status should be False!"
            )
            self.assertEqual(
                "The password is not meeting the length and/or characters"
                " requirements!",
                response_message["message_password"],
                "The message is not expected!",
            )

    def test_password_not_compliant_with_maximum_length(self):
        with self.app.app_context():
            password = self.fake.password(
                length=self.max_length + 1,
                special_chars=self.has_symbols,
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )

            payload = {}
            user_token = BaseTestClass.get_user().token
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected!",
            )
            self.assertFalse(
                response_message["status"], "The status should be False!"
            )
            self.assertEqual(
                "The password is not meeting the length and/or characters"
                " requirements!",
                response_message["message_password"],
                "The message is not expected!",
            )

    def test_password_not_compliant_with_digits(self):
        with self.app.app_context():
            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=self.has_symbols,  # nosec B311
                digits=(not self.has_digits),
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )

            payload = {}
            user_token = BaseTestClass.get_user().token
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected!",
            )
            self.assertFalse(
                response_message["status"], "The status should be False!"
            )
            self.assertEqual(
                "The password is not meeting the length and/or characters"
                " requirements!",
                response_message["message_password"],
                "The message is not expected!",
            )

    def test_password_not_compliant_with_symbols(self):
        with self.app.app_context():
            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=(not self.has_symbols),  # nosec B311
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )

            payload = {}
            user_token = BaseTestClass.get_user().token
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected!",
            )
            self.assertFalse(
                response_message["status"], "The status should be False!"
            )
            self.assertEqual(
                "The password is not meeting the length and/or characters"
                " requirements!",
                response_message["message_password"],
                "The message is not expected!",
            )

    def test_password_not_compliant_with_uppercase(self):
        with self.app.app_context():
            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=self.has_symbols,  # nosec B311
                digits=self.has_digits,
                upper_case=(not self.has_uppercase),
                lower_case=self.has_lowercase,
            )

            payload = {}
            user_token = BaseTestClass.get_user().token
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected!",
            )
            self.assertFalse(
                response_message["status"], "The status should be False!"
            )
            self.assertEqual(
                "The password is not meeting the length and/or characters"
                " requirements!",
                response_message["message_password"],
                "The message is not expected!",
            )

    def test_password_not_compliant_with_lowercase(self):
        with self.app.app_context():
            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=self.has_symbols,  # nosec B311
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=(not self.has_lowercase),
            )

            payload = {}
            user_token = BaseTestClass.get_user().token
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = self.characteristics[
                "min_accepted_score"
            ]

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected!",
            )
            self.assertFalse(
                response_message["status"], "The status should be False!"
            )
            self.assertEqual(
                "The password is not meeting the length and/or characters"
                " requirements!",
                response_message["message_password"],
                "The message is not expected!",
            )

    def test_password_not_compliant_with_min_complexity_score(self):
        with self.app.app_context():
            password = self.fake.password(  # nosec B311
                length=random.randrange(
                    self.min_length, self.max_length
                ),  # nosec B311
                special_chars=self.has_symbols,  # nosec B311
                digits=self.has_digits,
                upper_case=self.has_uppercase,
                lower_case=self.has_lowercase,
            )

            payload = {}
            user_token = BaseTestClass.get_user().token
            payload["api_key"] = user_token
            payload["password"] = password
            payload["characteristics"] = self.characteristics[
                "characteristics"
            ]
            payload["min_accepted_score"] = 1000

            response = self.client.post(
                ROUTE_PASSWORD_SCORING,
                json=payload,
            )
            response_message = json.loads(response.text)
            self.assertEqual(
                200,
                response.status_code,
                "The response status code is unexpected!",
            )
            self.assertFalse(
                response_message["status"],
                "The status should be False! calculated score is {} for"
                " password => {}".format(response_message["score"], password),
            )
            self.assertEqual(
                "The strength of the password is too low!",
                response_message["message_score"],
                "The message socre is not expected!",
            )

    def test_score_color_black(self):
        score = 15.00
        resulting_color = ColorScore.get_color_from_score(score)
        self.assertEqual(
            "black",
            resulting_color,
            "A score of 15 should give a black color!",
        )

    def test_score_color_crimson(self):
        score = 62.00
        resulting_color = ColorScore.get_color_from_score(score)
        self.assertEqual(
            "crimson",
            resulting_color,
            "A score of 62 should give a crimson color!",
        )

    def test_score_color_coral(self):
        score = 90.01
        resulting_color = ColorScore.get_color_from_score(score)
        self.assertEqual(
            "coral",
            resulting_color,
            "A score of 90 should give a coral color!",
        )

    def test_score_color_yellow(self):
        score = 100.23
        resulting_color = ColorScore.get_color_from_score(score)
        self.assertEqual(
            "yellow",
            resulting_color,
            "A score of 100 should give a yellow color!",
        )

    def test_score_color_yellowgreen(self):
        score = 106.87
        resulting_color = ColorScore.get_color_from_score(score)
        self.assertEqual(
            "yellowgreen",
            resulting_color,
            "A score of 106 should give a yellowgreen color!",
        )

    def test_score_color_lightgreen(self):
        score = 120.12
        resulting_color = ColorScore.get_color_from_score(score)
        self.assertEqual(
            "lightgreen",
            resulting_color,
            "A score of 106 should give a lightgreen color!",
        )

    def test_score_color_lime(self):
        score = 156.06
        resulting_color = ColorScore.get_color_from_score(score)
        self.assertEqual(
            "lime", resulting_color, "A score of 106 should give a lime color!"
        )
