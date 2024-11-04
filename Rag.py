from main import SearchEngine
import pandas as pd
import os
import google.generativeai as genai
google_gemini_api = "AIzaSyBN4k_ZQoBhNbBdHB7PHGWRL6PD_gHQ5Yk"

class GenAIClient:
    def __init__(self, google_gemini_api=google_gemini_api):
        os.environ["GOOGLE_API_KEY"] = google_gemini_api
        genai.configure(api_key=google_gemini_api)

    def chat(self, messages):
        model = genai.GenerativeModel("gemini-1.5-pro")
        responses = model.generate_content(messages)
        return responses.text

prompt_template_format = (
                        "### Instruction:\n{instruction}\\n"
    "### Input:\n{input}\n"
    "### Response:\n{output}")


def get_prompt(questions, contexts):
    contexts = "\n".join([f"Context [{i+1}]: {x['content']}" for i, x in enumerate(contexts)])
    instruction = (
        "Bạn là một nhân viên tư vấn về phim, với nhiệm vụ cung cấp câu trả lời đầy đủ, và chính xác."
        "Nếu trong ngữ cảnh không có thông tin yêu cầu, hãy đưa ra phản hồi lịch sự, nhưng không đề cập rằng thông tin không có sẵn.")
    input = ("Dựa trên ngữ cảnh cùng với hội thoại gần nhất(nếu có) dưới đây, hãy trả lời câu hỏi ở cuối."
             "Trong câu trả lời: "
            "-Không được lấy thông tin hay dữ liệu bên ngoài."
            "-Không sử dụng những cụm từ như 'Dựa trên những thông tin, văn bản, ngữ cảnh được đề cập, cung cấp' hoặc cách diễn đạt nào tương tự."
             "\nNgữ cảnh:\n{}\nCâu hỏi: {}").format(contexts, questions)
    prompt = prompt_template_format.format(instruction=instruction, input=input, output="")
    return prompt
class Rag:
    def __init__(self, questions,data="data.csv", top_k=3):
        self.data = pd.read_csv(data)
        self.questions = questions
        self.top_k = top_k
        self.llm = GenAIClient()
    def generate_text(self):
        new_questions = SearchEngine(self.data).hybrid_search(self.questions, top_n=self.top_k)
        print(new_questions)
        new_questions = get_prompt(self.questions, new_questions)
        print(new_questions)
        return self.llm.chat(new_questions)

if __name__ == '__main__':
    query = "Mình rất thích Dương Tử. Bạn có thể đề xuất cho mình bộ phim do cô ấy thủ vai không?"
    chat = Rag(questions=query)
    print(chat.generate_text())