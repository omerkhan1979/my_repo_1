import unittest
import google.generativeai as genai

class TestGenerativeAI(unittest.TestCase):
    """
    A test case for the GenerativeAI class.

    This test case includes various test methods to ensure the functionality of the GenerativeAI class.
    """

    def test_model_instantiation(self):
        model = genai.GenerativeModel(model="chat-bison-001")
        self.assertIsInstance(model, genai.GenerativeModel)

    def test_temperature_setting(self):
        model = genai.GenerativeModel(model="chat-bison-001")
        model.temperature = 0.5
        self.assertEqual(model.temperature, 0.5)

    def test_top_p_setting(self):
        model = genai.GenerativeModel(model="chat-bison-001")
        model.top_p = 0.8
        self.assertEqual(model.top_p, 0.8)

    def test_top_k_setting(self):
        model = genai.GenerativeModel(model="chat-bison-001")
        model.top_k = 30
        self.assertEqual(model.top_k, 30)

    def test_generate_text(self):
        model = genai.GenerativeModel(model="chat-bison-001")
        prompt = "What is the capital of France?"
        response = model.generate_text(prompt=prompt)
        self.assertIsNotNone(response.result)

if __name__ == "__main__":
    unittest.main()
