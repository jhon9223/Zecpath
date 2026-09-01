from django.contrib import admin

from .models import (
    AICall,
    AIInterviewSession,
    AIQuestion,
    AIAnswer,
    CallLog,
)


admin.site.register(AICall)
admin.site.register(AIInterviewSession)
admin.site.register(AIQuestion)
admin.site.register(AIAnswer)
admin.site.register(CallLog)
