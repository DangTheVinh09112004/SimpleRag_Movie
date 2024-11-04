from Rag import GenAIClient
from collections import deque
DEFAULT_SUMMARY_LIMIT = 2
class ConversationHistory:
    def __init__(self):
        self.history = deque(maxlen=DEFAULT_SUMMARY_LIMIT)

    def add_messages(self, questions, contents):
        self.history.append({"questions": questions, "contents": contents})

    def get_full_history(self):
        return list(self.history)
class SummarizedMemory:
    def __init__(self, llm=GenAIClient()):
        self.llm = llm
        self.summaries = []
        self.history_count = 0

    def summarize_if_threshold_met(self, conversation_history, threshold=2):
        if len(conversation_history.history) >= threshold and self.history_count < len(conversation_history.history):
            history_text = "\n".join(
                [f"{entry['questions']}: {entry['contents']}" for entry in conversation_history.get_full_history()]
            )
            prompt = (
                "Tóm tắt lại các thông tin chính từ cuộc hội thoại sau đây:\n"
                "{}\nBản tóm tắt:".format(history_text)
            )
            summary = self.llm.chat(prompt)
            self.summaries.append(summary)
            self.history_count = len(conversation_history.history)
            return summary
        else:
            return self.get_current_summary()

    def get_current_summary(self):
        return self.summaries[-1] if self.summaries else "Chưa có tóm tắt nào."

    def get_recent_message(self, conversation_history, n=1):
        if n <= 0:
            return []
        return list(conversation_history.history)[-n:]