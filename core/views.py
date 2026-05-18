from django.shortcuts import render

def about(request):
    return render(request, "core/about.html")

def disciplines(request):
    return render(request, "core/disciplines.html")

def equipment(request):
    return render(request, "core/equipment.html")

def age_categories(request):
    return render(request, "core/age_categories.html")

def staff(request):
    return render(request, "core/staff.html")