from Rag import GenAIClient
llm = GenAIClient()
def is_relevant(summary: str, query: str):
    prompt = ("Dưới đây là 1 đoạn hội thoại gần nhất và câu hỏi của người dùng. "
              "Kiểm tra xem nếu câu hỏi liên quan đến đoạn hội thoại gần nhất thì trả lời có, không thì trả lời không. "
              "Chú ý rằng chỉ được trả lời có hoặc không.\n\n"
              "Hội thoại gần nhất: {}\n"
              "Truy vấn: {}\n"
              "Trả lời:").format(summary, query)
    response = llm.chat(messages=prompt).strip()
    return response.lower() == "có"

if __name__ == '__main__':
    summary = "Mình rất thích Dương Tử. Bạn có thể đề xuất cho mình bộ phim do cô ấy thủ vai không?Có, Dương Tử đóng trong phim Trường Tương Tư (Phần 2) và Thừa Hoan Ký. "
    query = "nói cho mình nội dung của 2 bộ phim trên"
    print(is_relevant(summary, query))