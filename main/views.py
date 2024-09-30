from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .forms import UserRegisterForm, ArtworkUploadForm, CommentForm
from .models import Artwork

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('profile')  # Redirect to profile after registration
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

class ArtworkListView(ListView):
    model = Artwork
    template_name = 'home.html'
    context_object_name = 'artworks'
    paginate_by = 10
    ordering = ['-created_at']

class ArtworkCreateView(LoginRequiredMixin, CreateView):
    model = Artwork
    form_class = ArtworkUploadForm
    template_name = 'artwork_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ArtworkDetailView(DetailView):
    model = Artwork
    template_name = 'artwork_detail.html'
    context_object_name = 'artwork'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_list = self.get_object().comments.all()
        paginator = Paginator(comments_list, 5)
        page = self.request.GET.get('page')
        comments = paginator.get_page(page)
        context['comments'] = comments
        context['form'] = CommentForm()
        context['artwork_id'] = self.get_object().id  # Добавьте эту строку
        return context

    def post(self, request, *args, **kwargs):
        artwork = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.artwork = artwork
            comment.author = request.user
            comment.save()
            return redirect('artwork-detail', id=artwork.id)
        context = self.get_context_data(artwork=artwork, form=form)
        return self.render_to_response(context)
