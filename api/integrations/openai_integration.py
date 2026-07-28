import openai

class OpenAIIntegration:
    @staticmethod
    def get_completion(messages, model="gpt-4", temperature=0.7):
        return openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
