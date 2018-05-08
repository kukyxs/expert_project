from rest_framework import generics, renderers, parsers, authentication, permissions, status
from rest_framework.response import Response

from expert_skill.models import Category
from expert_skill.serializers import CategorySerializer


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = ()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser)

    def get(self, request, *args, **kwargs):
        return super(CategoriesView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if request.user.is_staff:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"code": 403, "message": "Has No Permission"}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


