
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from applications.models import JobApplication
from .models import Conversation
from .serializers import ConversationSerializer, MessageSerializer


def get_user_conversations(user):
    """Return conversations that belong to the authenticated participant."""
    if user.role == User.CANDIDATE:
        return Conversation.objects.filter(
            candidate=user
        ).select_related("application", "recruiter", "candidate")

    if user.role == User.EMPLOYER:
        return Conversation.objects.filter(
            recruiter=user
        ).select_related("application", "recruiter", "candidate")

    return Conversation.objects.none()


class ConversationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in [User.CANDIDATE, User.EMPLOYER]:
            return Response(
                {"detail": "You are not allowed to access chats."},
                status=status.HTTP_403_FORBIDDEN,
            )

        conversations = get_user_conversations(request.user).order_by(
            "-updated_at"
        )

        serializer = ConversationSerializer(
            conversations,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class StartConversationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, application_id):
        if request.user.role not in [User.CANDIDATE, User.EMPLOYER]:
            return Response(
                {"detail": "You are not allowed to start a chat."},
                status=status.HTTP_403_FORBIDDEN,
            )

        application = get_object_or_404(
            JobApplication.objects.select_related(
                "candidate__user",
                "job__employer__user",
            ),
            pk=application_id,
        )

        candidate_user = application.candidate.user
        recruiter_user = application.job.employer.user

        if request.user.role == User.CANDIDATE:
            # Candidates can initiate only for their own shortlisted application.
            if candidate_user.pk != request.user.pk:
                return Response(
                    {"detail": "You cannot access this application."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if application.status != JobApplication.SHORTLISTED:
                return Response(
                    {
                        "detail": (
                            "You can start a conversation only after "
                            "being shortlisted."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        elif request.user.pk != recruiter_user.pk:
            # Recruiters can contact only applicants for their own jobs.
            return Response(
                {"detail": "You cannot access this application."},
                status=status.HTTP_403_FORBIDDEN,
            )

        conversation, created = Conversation.objects.get_or_create(
            application=application,
            defaults={
                "recruiter": recruiter_user,
                "candidate": candidate_user,
            },
        )

        # Protect against inconsistent participant data.
        if (
            conversation.recruiter_id != recruiter_user.pk
            or conversation.candidate_id != candidate_user.pk
        ):
            return Response(
                {"detail": "Conversation participants do not match."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = ConversationSerializer(
            conversation,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


class MessageListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_conversation(self, request, conversation_id):
        # Return 404 for conversations the user does not participate in.
        return get_object_or_404(
            get_user_conversations(request.user),
            pk=conversation_id,
        )

    def get(self, request, conversation_id):
        if request.user.role not in [User.CANDIDATE, User.EMPLOYER]:
            return Response(
                {"detail": "You are not allowed to access chats."},
                status=status.HTTP_403_FORBIDDEN,
            )

        conversation = self.get_conversation(
            request, conversation_id
        )

        messages = conversation.messages.select_related(
            "sender"
        ).order_by("created_at", "pk")

        serializer = MessageSerializer(messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, conversation_id):
        if request.user.role not in [User.CANDIDATE, User.EMPLOYER]:
            return Response(
                {"detail": "You are not allowed to send messages."},
                status=status.HTTP_403_FORBIDDEN,
            )

        conversation = self.get_conversation(
            request, conversation_id
        )

        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(
            conversation=conversation,
            sender=request.user,
        )

        conversation.save(update_fields=["updated_at"])

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
