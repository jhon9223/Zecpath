from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import extract_resume_text, clean_resume_text


class ResumeParseAPIView(APIView):

    permission_classes = [IsAuthenticated]

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

            return Response({
                "filename": file.name,
                "text": cleaned_text
            })

        except ValueError as e:

            return Response(
                {"error": str(e)},
                status=400
            )
