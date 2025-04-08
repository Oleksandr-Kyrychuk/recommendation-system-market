class RecommendationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
  
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price']
