from restlib import resources
from django.http import HttpResponse
from pyPdf import PdfFileWriter, PdfFileReader
import StringIO
import requests

class PDFAppender(resources.Resource):

    # This assumes a query string is used where a pdfs param
    # is repeatedly used for each PDF we need to concat.
    # Django will create a QueryDict with a pdfs attribute
    # containing all instances of the pdfs attributes used
    # in the query string
    def GET(self, request):
        # getlist here will return a list of all the query string paramaters
        # named 'pdfs'
        urls = request.GET.getlist("pdfs")
        if not urls:
            items = request.GET.items()
            items.sort(key=lambda x: x[0])
            urls = []
            for key, value in items:
               urls.append(value)
        
        s = requests.session()
        responses = [s.get(url, prefetch=True) for url in urls]

        master_pdf = PdfFileWriter()
        # Iterate over each response and add it to the master PDF
        for response in responses:
            # pyPDF needs a file like object
            input = PdfFileReader(StringIO.StringIO(response.content))

            # Add this whole PDF to the master PDF
            for page_no in range(0, input.numPages):
                master_pdf.addPage(input.getPage(page_no))

        output = HttpResponse(content_type="application/pdf")
        master_pdf.write(output)
        return output
