from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Product
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import torch
from torchvision import models, transforms

# Завантажуємо pretrained ResNet
resnet = models.resnet50(pretrained=True)
resnet.eval()  # Режим оцінки
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_image_features(image_url):
    """Отримує візуальні ознаки зображення через ResNet"""
    try:
        response = requests.get(image_url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        img_tensor = preprocess(img).unsqueeze(0)  # Додаємо батч-розмір
        with torch.no_grad():
            features = resnet(img_tensor)  # Отримуємо вектор ознак
        return features.numpy().flatten()
    except Exception:
        return None  # Повертаємо None у разі помилки

def get_recommendations(product_id, num_recommendations=5):
    products = Product.objects.all()
    if not products.exists():
        return []

    # Текстова частина
    texts = [
        f"{product.name} {product.description} {product.category.name if product.category else ''}"
        for product in products
    ]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    target_product = Product.objects.get(id=product_id)
    target_idx = list(products).index(target_product)
    text_similarity = cosine_similarity(tfidf_matrix[target_idx], tfidf_matrix).flatten()
    
    # Візуальна частина
    target_image = target_product.images.first()
    if target_image:
        target_features = get_image_features(target_image.image_url)
    else:
        target_features = None
    
    visual_similarity = np.zeros(len(products))
    if target_features is not None:
        for i, product in enumerate(products):
            product_image = product.images.first()
            if product_image:
                product_features = get_image_features(product_image.image_url)
                if product_features is not None:
                    visual_similarity[i] = cosine_similarity([target_features], [product_features])[0][0]
    
    # Комбінуємо схожість
    if target_features is not None and np.max(visual_similarity) > 0:
        combined_similarity = 0.7 * text_similarity + 0.3 * visual_similarity
    else:
        combined_similarity = text_similarity
    
    similar_indices = combined_similarity.argsort()[-(num_recommendations + 1):-1][::-1]
    return [products[i] for i in similar_indices]
