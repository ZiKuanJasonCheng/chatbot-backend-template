import functools
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SentenceBert:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    #@functools.lru_cache(1000)
    def __call__(self, list_text, to_tensor=False):
        arr_text_embedded = self.model.encode(list_text, convert_to_tensor=to_tensor)
        return arr_text_embedded

def calculate_similarity_index(target, pool):
    similarities = cosine_similarity(target, pool).squeeze()
    idx_sorted = np.argsort(similarities, kind="quicksort")[::-1]
    return idx_sorted, similarities

if __name__ == "__main__":
    pass
