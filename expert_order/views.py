import datetime

from django.db import transaction
from django_filters import rest_framework
from rest_framework import permissions, authentication, parsers, renderers, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from expert_order.models import Order
from expert_order.serializers import PublishOrderSerializer, OrdersSerializer, PickFinishOrderSerializer, \
    EvaluateSerializer
from expert_user.models import ExUser


# 发布订单
class PublishOrderView(APIView):
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

    def post(self, request, format='json'):
        serializer = PublishOrderSerializer(data=request.data)

        if serializer.is_valid():
            order = serializer.save()
            ex_user = ExUser.objects.get(user=request.user)
            Order.objects.filter(id=order.id).update(owner=ex_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 筛选发布的订单，接的订单，不同状态的订单
class OrdersView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filter_fields = ['owner', 'picker', 'order_state']

    def get(self, request, *args, **kwargs):
        return super(OrdersView, self).get(self, request, *args, **kwargs)


# 查看详情
class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)


# 删除订单
class OrderDeleteView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

    def delete(self, request, *args, **kwargs):
        ex_user = ExUser.objects.get(user=request.user)
        try:
            order = Order.objects.get(pk=kwargs['pk'])
        except Order.DoesNotExist:
            return Response({"code": 404, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if not (ex_user == order.owner):
            return Response({"code": 403, "message": "Not owner"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if order.order_state == 0:
                Order.objects.filter(id=kwargs['pk']).delete()
                return Response({"code": 200, "message": "Canceled Succeed"}, status.HTTP_200_OK)
            return Response({"code": 404, "message": "Could't cancel the order"},
                            status=status.HTTP_400_BAD_REQUEST)


# 修改订单信息
class OrderUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.filter(order_state=0)
    serializer_class = PublishOrderSerializer
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

    def update(self, request, *args, **kwargs):
        ex_user = ExUser.objects.get(user=request.user)
        try:
            order = Order.objects.get(pk=kwargs['pk'])
        except Order.DoesNotExist:
            return Response({"code": 404, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        print('user is {} and order is {}'.format(ex_user, order))

        if not (ex_user == order.owner):
            return Response({"code": 403, "message": "Not owner"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if order.order_state == 0:
                serializer = self.serializer_class(order, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"code": 404, "message": "Could't update the order"},
                                status=status.HTTP_400_BAD_REQUEST)


# 接单
class PickOrderView(APIView):
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

    def put(self, request, pk, format='json'):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"code": 404, "message": "The Order is not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PickFinishOrderSerializer(data=request.data)

        if serializer.is_valid():
            ex_user = ExUser.objects.get(user=request.user)
            if order.owner == ex_user:
                return Response({"code": 404, "message": "Picker can't be the owner"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if order.order_state == 0:
                    with transaction.atomic():
                        Order.objects.filter(pk=pk).update(picker=ex_user, order_state=1,
                                                           picked_time=datetime.datetime.now())
                        return Response({"code": 200, "message": "Pick Succeed"}, status=status.HTTP_200_OK)
                return Response({"code": 404, "message": "Error State"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 完工
class FinishOrderView(APIView):
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

    def put(self, request, pk, format='json'):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"code": 404, "message": "The Order is not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PickFinishOrderSerializer(order, data=request.data)

        if serializer.is_valid():
            ex_user = ExUser.objects.get(user=request.user)
            if order.picker == ex_user:
                if order.order_state == 1:
                    Order.objects.filter(pk=pk).update(order_state=2, finished_time=datetime.datetime.now())
                    return Response({"code": 200, "message": "Finish Order Succeed"}, status=status.HTTP_200_OK)
                return Response({"code": 404, "message": "Error State"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"code": 401, "message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 评价
class EvaluateView(APIView):
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

    def put(self, request, pk, format='json'):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"code": 404, "message": "The Order is not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EvaluateSerializer(order, data=request.data)
        if serializer.is_valid():
            ex_user = ExUser.objects.get(user=request.user)
            if order.owner == ex_user:
                if order.order_state == 2:
                    serializer.save()
                    Order.objects.filter(pk=pk).update(order_state=3, evaluate_time=datetime.datetime.now())
                    return Response({"code": 200, "message": "Evaluate Succeed"}, status=status.HTTP_200_OK)
                return Response({"code": 404, "message": "Error State"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"code": 401, "message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
