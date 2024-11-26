from django.contrib import admin

from crm.models import User, FAQArticle, SupportAgent, SupportCategory, SupportChannel, Ticket, TicketComment

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 1

class TicketAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "created_at", "updated_at"]
    fieldsets = [
        ("General information", {"fields": ["title", "status"]}),
    ] 
    inlines = [TicketCommentInline]
    list_filter = ["created_at"]
    search_fields = ["title", "status"]


# Register your models here.
#admin.site.register(User)
#admin.site.register(SupportAgent) 
admin.site.register(FAQArticle) 
admin.site.register(SupportCategory) 
admin.site.register(SupportChannel)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketComment) 