from django.shortcuts import render
from main.forms import UploadImageForm
from profin_site import settings
import imgsegment
import mahotas

# Create your views here.
def index(request):
	if request.method == "POST":
		form = UploadImageForm(request.POST, request.FILES)
		if form.is_valid():
			with open(settings.MEDIA_ROOT+request.FILES['image'].name, 'wb+') as destination:
				for chunk in request.FILES['image'].chunks():
					destination.write(chunk)
		return render(request, 'index.html', {"form": form, "img":request.FILES['image'].name})
	else:
		form = UploadImageForm()
		return render(request, 'index.html', {"form": form})

def segment(request):
	if request.method == "POST":
		min_size = int(request.POST['min']) if request.POST['min'] else 1500
		max_size = int(request.POST['max']) if request.POST['max'] else 18000
		img_name = request.POST['img_name']
		img = mahotas.imread(settings.MEDIA_ROOT+img_name)
		filename = img_name.split(".")[0]
		imgsegment.segment(img, filename, min_size = min_size, max_size = max_size)
		return render(request, 'segment.html', {"smg_img":'%s-combined.jpg' % filename, "img_name":img_name, "min":min_size, "max":max_size})
	else:
		img_name = request.GET['img_name']
		img = mahotas.imread(settings.MEDIA_ROOT+img_name)
		filename = img_name.split(".")[0]
		imgsegment.segment(img, filename)
		return render(request, 'segment.html', {"smg_img":'%s-combined.jpg' % filename, "img_name":img_name})

def result(request):
	return render(request, 'result.html')
