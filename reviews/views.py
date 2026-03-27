from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer
from rest_framework import status
# 🔹 GET REVIEWS
@api_view(['GET'])
def get_reviews(request):
    provider_id = request.GET.get('provider')

    if not provider_id:
        return Response({"error": "Provider ID required"})

    reviews = Review.objects.filter(provider_id=provider_id).order_by('-created_at')

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# 🔹 ADD REVIEW
@api_view(['POST'])
def add_review(request):
    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)
# 🔹 DELETE REVIEW
@api_view(['DELETE'])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
        review.delete()
        return Response({"message": "Deleted"}, status=200)
    except Review.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
# 🔹 UPDATE REVIEW
@api_view(['PUT'])
def update_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
        serializer = ReviewSerializer(review, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    except Review.DoesNotExist:
        return Response({"error": "Not found"}, status=404)