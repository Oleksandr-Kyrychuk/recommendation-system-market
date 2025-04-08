from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Product

def get_reccomendations(product_id, num_reccomendations = 5):
    products = Product.object.all()
    if not products.exist():
      return []


  texts = [ 
    f"{product.description} {product.category.name if product.category else ''}"
    for product in products
  ]

  #Векторизація тексту
  vectorizer = TfidfVectorizer()
  tfidf_matrix = vectorizer.fit_transform(texts)

  #індекс цільового товару
  target_product = Product.objects.get(id=product_id)
  target_idx = list(products).index(target_product)

  similarity_scores = cosine_similarity(tfidf_matrix[target_idx], tfidf_matrix).flatten()

  #Сорт і отримання топ-N
  similar_indices = similarity_scores.argsort()[-(num_recomendations + 1):-1][::-1]

  recommended_products = [products[i] for i in similar_indices]
  return recommended_products
  
