from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiTypes

from accounts.permissions import IsEmployer, IsCandidate

from .services import extract_resume_text, clean_resume_text, parse_resume


class ResumeParseRequestSerializer(serializers.Serializer):
    resume = serializers.FileField()


class ResumeParseErrorSerializer(serializers.Serializer):
    error = serializers.CharField()


class ResumeParseResponseSerializer(serializers.Serializer):
    filename = serializers.CharField()
    text = serializers.CharField()
    parsed_data = serializers.JSONField()


class ResumeParseAPIView(APIView):

    permission_classes = [IsAuthenticated, IsEmployer | IsCandidate]

    @extend_schema(
        summary="Parse resume",
        description=(
            "Upload a resume file to extract and clean its text, "
            "then return the parsed resume data."
        ),
        request=ResumeParseRequestSerializer,
        responses={
            200: ResumeParseResponseSerializer,
            400: ResumeParseErrorSerializer,
        },
    )
    def post(self, request):

        file = request.FILES.get("resume")

        if not file:
            return Response(
                {"error": "Resume file is required."},
                status=400
            )

        try:
            text = extract_resume_text(file)

            cleaned_text = clean_resume_text(text)
            parsed_data = parse_resume(cleaned_text)
            return Response({
                "filename": file.name,
                "text": cleaned_text,
                "parsed_data": parsed_data
            })

        except ValueError as e:

            return Response(
                {"error": str(e)},
                status=400
            )
