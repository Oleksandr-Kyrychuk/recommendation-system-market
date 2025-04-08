from rest_framework.views import APIView
from .recommendations import get_recommendations
from .serializers import RecommendationSerializer

class RecommendationView(APIView):
    def get(self, request, product_id):
        try:
            recommended_products = get_recommendations(product_id)
            serializer = RecommendationSerializer(recommended_products, many=True)
            return Response({"recommendations": serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
