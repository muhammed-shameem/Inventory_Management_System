from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView

class LandingView(TemplateView):
    template_name = 'landing_page.html'
    
class CustomLoginView(LoginView):
    template_name = 'login.html'