from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pandas as pd
import re
import numpy as np
import pickle
import os
DEFAULT_SEARCH_LIMIT = 5
class SearchEngine:
    def __init__(self, data, embedding_model_name="bkai-foundation-models/vietnamese-bi-encoder", embeddings_file="embeddings.pkl"):
        self.data = data
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.data['Nội dung phim'])
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embeddings_file = embeddings_file
        self.split_sentences()
        if os.path.exists(self.embeddings_file):
            self.load_embeddings()
        else:
            self.embeddings = self.embedding_model.encode(self.sentences, show_progress_bar=True)
            self.embeddings /= np.linalg.norm(self.embeddings, axis=1)[:, np.newaxis]
            self.save_embeddings()
    def split_sentences(self):
        self.sentences = []
        self.original_content_map = {}
        for idx, content in enumerate(self.data['Nội dung phim']):
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
            self.sentences.extend(sentences)
            for sentence in sentences:
                self.original_content_map[sentence] = content
    def save_embeddings(self):
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump((self.sentences, self.embeddings), f)
    def load_embeddings(self):
        with open(self.embeddings_file, 'rb') as f:
            self.sentences, self.embeddings = pickle.load(f)

    def search_keyword(self, query, top_n=DEFAULT_SEARCH_LIMIT):
        query_vector = self.vectorizer.transform([query])
#        query_vector /= np.linalg.norm(query_vector, axis=1)[:, np.newaxis]
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        related_docs_indices = cosine_similarities.argsort()[:-top_n - 1:-1]
        results = self.data.iloc[related_docs_indices].drop_duplicates(subset=['Nội dung phim'])
        if len(results) < top_n:
            additional_indices = [idx for idx in related_docs_indices if idx not in results.index]
            additional_needed = top_n - len(results)
            additional_results = self.data.iloc[additional_indices[:additional_needed]]
            results = pd.concat([results, additional_results])
        return results.head(top_n)
    def search_vector(self, query, top_n=DEFAULT_SEARCH_LIMIT):
        query_embedding = self.embedding_model.encode([query])
        query_embedding /= np.linalg.norm(query_embedding, axis=1)[:, np.newaxis]
        cosine_similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        related_sentence_indices = cosine_similarities.argsort()[:-top_n - 1:-1]
        seen_contents = set()
        results = []
        for idx in related_sentence_indices:
            sentence = self.sentences[idx]
            original_content = self.original_content_map[sentence]
            if original_content not in seen_contents:
                seen_contents.add(original_content)
                original_row = self.data[self.data['Nội dung phim'] == original_content].iloc[0]
                results.append(original_row)
            if len(results) >= top_n:
                break
        return pd.DataFrame(results).drop_duplicates(subset=['Nội dung phim'])
    def weighted_reciprocal_rank(self, doc_lists):
        c = 60
        weights = [1] * len(doc_lists)
        all_documents = set()
        for doc_list in doc_lists:
            for doc in doc_list:
                all_documents.add(doc["content"])
        rrf_score_dic = {doc: 0.0 for doc in all_documents}
        for doc_list, weight in zip(doc_lists, weights):
            for rank, doc in enumerate(doc_list, start=1):
                rrf_score = weight * (1 / (rank + c))
                rrf_score_dic[doc["content"]] += rrf_score
        sorted_documents = sorted(rrf_score_dic.keys(), key=lambda x: rrf_score_dic[x], reverse=True)
        page_content_to_doc_map = {
            doc["content"]: doc for doc_list in doc_lists for doc in doc_list
        }
        sorted_docs = [
            page_content_to_doc_map[page_content] for page_content in sorted_documents
        ]
        return sorted_docs
    def hybrid_search(self, query, top_n=DEFAULT_SEARCH_LIMIT):
        keyword_results = self.search_keyword(query, top_n=top_n).to_dict(orient="records")
        vector_results = self.search_vector(query, top_n=top_n).to_dict(orient="records")
        doc_lists = [keyword_results, vector_results]
        for i in range(len(doc_lists)):
            doc_lists[i] = [
                {
                    "title": doc["Tên phim"],
                    "content": doc["Nội dung phim"],
#                    "score": 1,
                }
                for doc in doc_lists[i]
            ]
        fused_documents = self.weighted_reciprocal_rank(doc_lists)
        return fused_documents[:top_n]
def main():
    file_path = "data.csv"
    data = pd.read_csv(file_path)
    search_engine = SearchEngine(data, embedding_model_name='bkai-foundation-models/vietnamese-bi-encoder')
    query = "Mình rất thích Dương Tử. Bạn có thể đề xuất cho mình bộ phim do cô ấy thủ vai không?"
    results = search_engine.hybrid_search(query)
    for a in range(len(results)):
        print(results[a])
if __name__ == "__main__":
    main()