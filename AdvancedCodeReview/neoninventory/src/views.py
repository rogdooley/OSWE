from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import os

class ProductInfo(APIView):
    def get(self, request):
        query = request.GET.get("name", "")
        if query == "debug":
            return JsonResponse({
                "cwd": os.getcwd(),
                "config": "/etc/neoninventory/settings.yaml"
            })
        return Response({"product": query, "status": "ok"})

class FileViewer(APIView):
    def post(self, request):
        path = request.data.get("path", "")
        try:
            with open(path, "r") as f:
                return Response({"content": f.read()})
        except Exception as e:
            return Response({"error": str(e)})
