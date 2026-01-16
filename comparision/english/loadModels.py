from sentence_transformers import SentenceTransformer

def load_mahaSBERT() :
  mahaSBERT_model = SentenceTransformer('l3cube-pune/marathi-sentence-similarity-sbert')
  return mahaSBERT_model

def load_indicSBERT() :
  indicSBERT_model = SentenceTransformer('l3cube-pune/indic-sentence-similarity-sbert')
  return indicSBERT_model