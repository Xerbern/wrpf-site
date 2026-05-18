from django.shortcuts import render
from django.utils.translation import gettext_lazy as _ 
from django.http import Http404

PDF_PAGES = {
    'rulebook': {
        'pdf_file': 'docs/rulebook.pdf',
        'title': _('WRPF Rule Book'),
    },
    'banned_substances': {
        'pdf_file': 'docs/banned_substances.pdf',
        'title': _('WRPF Banned Substances'),
    },
    'drug-testing-policies': {
        'pdf_file': 'docs/drug_testing_policies.pdf',
        'title': _('WRPF Drug Testing Policies'),
    },

}

def show_pdf(request, slug):
    page = PDF_PAGES.get(slug)
    if not page:
        raise Http404("Unknown PDF page")

    return render(request, 'rules/pdf_viewer.html', {
        'pdf_file': page['pdf_file'],
        'title': page['title'],
        'slug': slug,  # optional if you need it in the template
    })