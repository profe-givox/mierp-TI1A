from django.contrib import admin

from crm.models import User, FAQArticle, SupportAgent, SupportCategory, SupportChannel, Ticket, TicketComment

# class ChoiceInline(admin.TabularInline):
#     model = Choice
#     extra = 1

# class UserAdmin(admin.ModelAdmin):
#     list_display = ["question_text", "pub_date", "was_published_recently"]
#     fieldsets = [
#         ("General information", {"fields": ["question_text"]}),
#         ("Date information", {"fields": ["pub_date"]}),
#     ] 
#     inlines = [ChoiceInline]
#     list_filter = ["pub_date"]
#     search_fields = ["question_text"]


# Register your models here.
admin.site.register(User)
admin.site.register(SupportAgent) 
admin.site.register(FAQArticle) 
admin.site.register(SupportCategory) 
admin.site.register(SupportChannel) 