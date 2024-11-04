from flask import Flask, request, jsonify
from Rag import  Rag
from Summary import ConversationHistory, SummarizedMemory
from test_relevant import is_relevant

app = Flask(__name__)
conversation_history = ConversationHistory()
summary_memory = SummarizedMemory()
@app.route('/api/vinh_dep_trai/chat', methods=['POST'])

def ask_question():
    data = request.get_json()
    query = data.get('query', '')

    # Lấy tóm tắt hiện tại để làm ngữ cảnh
    context_summary = summary_memory.get_current_summary()

    # Kiểm tra xem câu hỏi có liên quan đến ngữ cảnh không
    if context_summary != "Chưa có tóm tắt nào." and is_relevant(context_summary, query):
        # Nếu có tóm tắt và câu hỏi liên quan, dùng tóm tắt làm ngữ cảnh
        full_context = f"Hội thoại gần nhất: {context_summary}\nCâu hỏi mới: {query}"
    else:
        # Nếu không có tóm tắt hoặc câu hỏi không liên quan
        recent_messages = summary_memory.get_recent_message(conversation_history)
        if recent_messages and is_relevant(recent_messages, query):
            # Tạo ngữ cảnh từ các tin nhắn gần nhất
            context_text = "\n".join(
                [f"{msg['questions']}: {msg['contents']}" for msg in recent_messages]
            )
            full_context = f"Hội thoại gần nhất: {context_text}\nCâu hỏi mới: {query}"
        else:
            # Nếu không có tin nhắn gần nhất, chỉ dùng câu hỏi mới
            full_context = query

    print(full_context)  # Kiểm tra ngữ cảnh đã ghép
    response = Rag(questions=full_context).generate_text()

    # Thêm câu hỏi và câu trả lời vào lịch sử hội thoại
    conversation_history.add_messages(query, response)

    # Tóm tắt nếu đạt ngưỡng và cập nhật bộ nhớ ngữ cảnh để dùng trong câu trả lời tiếp theo
    summary_memory.summarize_if_threshold_met(conversation_history)

    return jsonify({"response": response})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)