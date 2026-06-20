from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Review
from .serializers import ReviewSerializer


@api_view(["GET"])
def get_reviews(request):
    provider_id = request.GET.get("provider")
    if not provider_id:
        return Response({"error": "Provider ID required"})

    reviews = Review.objects.filter(provider_id=provider_id).order_by("-created_at")
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_review(request):
    review_data = request.data.copy()
    review_data["user"] = request.user.id
    serializer = ReviewSerializer(data=review_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id, user=request.user)
    except Review.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    review.delete()
    return Response({"message": "Deleted"}, status=200)


@api_view(["PUT", "POST"])
@permission_classes([IsAuthenticated])
def update_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id, user=request.user)
    except Review.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    review_data = request.data.copy()
    review_data["user"] = request.user.id
    serializer = ReviewSerializer(review, data=review_data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)
