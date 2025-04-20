import os

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from .models import Document, Category
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


# Home page view
@login_required(login_url='login')
def index(request):
    documents = Document.objects.all()

    # Filter documents by user access if not superuser
    if request.user.is_authenticated and not request.user.is_superuser:
        documents = documents.filter(accessible_by=request.user)

    # Group documents by category for easier access in template
    categories = Category.objects.all()

    context = {
        'documents': documents,
        'categories': categories,
    }
    return render(request, 'docsort/index.html', context)


# Login view
def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'docsort/login.html')


# Login processing view
def login_manager(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass1')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect('login')

    return redirect('login')


# Logout view
def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


# Upload document form view
@login_required(login_url='login')
def upload(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        keywords = request.POST.get('keywords')
        category_name = request.POST.get('category')

        # Get or create category
        category, created = Category.objects.get_or_create(name=category_name)

        # Create document
        document = Document(
            title=title,
            description=description,
            keywords=keywords,
            category=category,
            uploaded_by=request.user
        )

        # Handle file uploads
        if 'thumbnail' in request.FILES:
            document.thumbnail = request.FILES['thumbnail']

        if 'file1' in request.FILES:
            document.file1 = request.FILES['file1']

        if 'file2' in request.FILES:
            document.file2 = request.FILES['file2']

        document.save()

        # Add the current user to accessible_by
        document.accessible_by.add(request.user)

        messages.success(request, f"Document '{title}' uploaded successfully!")
        return redirect('index')

    context = {
        'categories': categories,
    }
    return render(request, 'docsort/upload.html', context)


# View for individual document
@login_required(login_url='login')
def document_detail(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)

    # Check if user has access
    if not document.can_access(request.user):
        messages.error(request, "You don't have permission to view this document.")
        return redirect('index')

    # Get keywords as a list
    keywords = document.get_keywords_list()

    context = {
        'document': document,
        'keywords': keywords,
    }
    return render(request, 'docsort/document_detail.html', context)


# Download handler
@login_required(login_url='login')
def download_file(request, doc_id, file_num):
    document = get_object_or_404(Document, id=doc_id)

    # Check if user has access
    if not document.can_access(request.user):
        messages.error(request, "You don't have permission to download this document.")
        return redirect('index')

    # Determine which file to download
    if file_num == 1 and document.file1:
        file_path = document.file1.path
        filename = os.path.basename(document.file1.name)
    elif file_num == 2 and document.file2:
        file_path = document.file2.path
        filename = os.path.basename(document.file2.name)
    else:
        messages.error(request, "Requested file does not exist.")
        return redirect('document_detail', doc_id=doc_id)

    # Open the file and create a FileResponse
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# Delete document handler
@login_required(login_url='login')
def delete_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    
    # Check if user is authorized to delete the document
    if not (request.user.is_superuser or request.user == document.uploaded_by):
        messages.error(request, "You don't have permission to delete this document.")
        return redirect('document_detail', doc_id=doc_id)
    
    if request.method == 'POST':
        title = document.title
        document.delete()
        messages.success(request, f"Document '{title}' has been deleted successfully.")
        return redirect('index')
    
    # If it's a GET request, redirect to document detail
    return redirect('document_detail', doc_id=doc_id)


# Edit document view
@login_required(login_url='login')
def edit_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    categories = Category.objects.all()
    
    # Check if user is authorized to edit the document
    if not (request.user.is_superuser or request.user == document.uploaded_by):
        messages.error(request, "You don't have permission to edit this document.")
        return redirect('document_detail', doc_id=doc_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        keywords = request.POST.get('keywords')
        category_name = request.POST.get('category')
        
        # Get or create category
        category, created = Category.objects.get_or_create(name=category_name)
        
        # Update document
        document.title = title
        document.description = description
        document.keywords = keywords
        document.category = category
        
        # Handle file uploads
        if 'thumbnail' in request.FILES:
            document.thumbnail = request.FILES['thumbnail']
            
        if 'file1' in request.FILES:
            document.file1 = request.FILES['file1']
            
        if 'file2' in request.FILES:
            document.file2 = request.FILES['file2']
        
        document.save()
        
        messages.success(request, f"Document '{title}' updated successfully!")
        return redirect('document_detail', doc_id=doc_id)
    
    # Get keywords as a list
    keywords = document.get_keywords_list()
    
    context = {
        'document': document,
        'categories': categories,
        'keywords': ", ".join(keywords),
    }
    return render(request, 'docsort/edit_document.html', context)