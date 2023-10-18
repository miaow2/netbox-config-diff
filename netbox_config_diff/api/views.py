from core.api.serializers import JobSerializer
from core.choices import JobStatusChoices
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_rq.queues import get_connection, get_queue
from netbox.api.viewsets import NetBoxModelViewSet, NetBoxReadOnlyModelViewSet
from netbox.constants import RQ_QUEUE_DEFAULT
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rq import Worker
from rq.exceptions import InvalidJobOperation
from utilities.exceptions import RQWorkerNotRunningException

from netbox_config_diff.choices import ConfigurationRequestStatusChoices
from netbox_config_diff.filtersets import (
    ConfigComplianceFilterSet,
    ConfigurationRequestFilterSet,
    PlatformSettingFilterSet,
    SubstituteFilterSet,
)
from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute

from .serializers import (
    ConfigComplianceSerializer,
    ConfigurationRequestRWSerializer,
    ConfigurationRequestScheduleSerializer,
    ConfigurationRequestSerializer,
    PlatformSettingSerializer,
    SubstituteSerializer,
)


class ConfigComplianceViewSet(NetBoxReadOnlyModelViewSet):
    queryset = ConfigCompliance.objects.prefetch_related("device")
    serializer_class = ConfigComplianceSerializer
    filterset_class = ConfigComplianceFilterSet


class PlatformSettingViewSet(NetBoxModelViewSet):
    queryset = PlatformSetting.objects.prefetch_related("platform", "tags")
    serializer_class = PlatformSettingSerializer
    filterset_class = PlatformSettingFilterSet


class ConfigurationRequestViewSet(NetBoxModelViewSet):
    queryset = ConfigurationRequest.objects.prefetch_related(
        "devices", "created_by", "approved_by", "scheduled_by", "tags"
    )
    serializer_class = ConfigurationRequestSerializer
    filterset_class = ConfigurationRequestFilterSet

    def create(self, request, *args, **kwargs):
        serializer = ConfigurationRequestRWSerializer(
            data=request.data | {"created_by": request.user.pk}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk):
        if not request.user.has_perm("netbox_config_diff.approve_configurationrequest"):
            raise PermissionDenied(
                "Approving configuration requests requires the "
                "netbox_config_diff.approve_configurationrequest permission."
            )

        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.finished:
            return Response(
                {"description": f"{obj} is finished, you can't change it."}, status=status.HTTP_400_BAD_REQUEST
            )

        if obj.approved_by:
            obj.approved_by = None
            obj.status = ConfigurationRequestStatusChoices.CREATED
            if obj.scheduled:
                obj.scheduled = None
                obj.scheduled_by = None
        else:
            obj.approved_by = get_user_model().objects.filter(pk=request.user.pk).first()
            obj.status = ConfigurationRequestStatusChoices.APPROVED
        obj.save()

        serializer = ConfigurationRequestSerializer(obj, context={"request": request})

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def schedule(self, request, pk):
        if not request.user.has_perm("netbox_config_diff.approve_configurationrequest"):
            raise PermissionDenied(
                "Scheduling configuration requests requires the"
                "netbox_config_diff.approve_configurationrequest permission."
            )

        if not Worker.count(get_connection(RQ_QUEUE_DEFAULT)):
            raise RQWorkerNotRunningException()

        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.finished:
            return Response(
                {"description": f"{obj} is finished, you can't change it."}, status=status.HTTP_400_BAD_REQUEST
            )
        if obj.scheduled:
            return Response({"description": f"{obj} already scheduled"}, status=status.HTTP_400_BAD_REQUEST)
        if obj.approved_by is None:
            return Response({"description": f"Approve {obj} before schedule."}, status=status.HTTP_400_BAD_REQUEST)

        input_serializer = ConfigurationRequestScheduleSerializer(data=request.data)
        if input_serializer.is_valid():
            obj.scheduled = input_serializer.validated_data.get("schedule_at")
            obj.status = ConfigurationRequestStatusChoices.SCHEDULED
            obj.scheduled_by = get_user_model().objects.filter(pk=request.user.pk).first()
            obj.save()
            serializer = ConfigurationRequestSerializer(obj, context={"request": request})
            obj.enqueue_job(request, "push_configs", schedule_at=input_serializer.validated_data.get("schedule_at"))
            return Response(serializer.data)

        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def unschedule(self, request, pk):
        if not request.user.has_perm("netbox_config_diff.approve_configurationrequest"):
            raise PermissionDenied(
                "Scheduling configuration requests requires the"
                "netbox_config_diff.approve_configurationrequest permission."
            )

        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.finished:
            return Response(
                {"description": f"{obj} is finished, you can't change it."}, status=status.HTTP_400_BAD_REQUEST
            )
        if obj.approved_by is None:
            return Response({"description": f"Approve {obj} before unschedule."}, status=status.HTTP_400_BAD_REQUEST)

        if obj.scheduled_by:
            obj.scheduled = None
            obj.scheduled_by = None
            obj.status = ConfigurationRequestStatusChoices.APPROVED
            obj.save()
            queue = get_queue(RQ_QUEUE_DEFAULT)
            for result in obj.jobs.filter(name__contains="push_configs", status=JobStatusChoices.STATUS_SCHEDULED):
                result.delete()
                if job := queue.fetch_job(str(result.job_id)):
                    try:
                        job.cancel()
                    except InvalidJobOperation:
                        pass

        serializer = ConfigurationRequestSerializer(obj, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="collect-diffs")
    def collect_diffs(self, request, pk):
        if not request.user.has_perm("netbox_config_diff.change_configurationrequest"):
            raise PermissionDenied(
                "Collecting diffs  requires the netbox_config_diff.change_configurationrequest permission."
            )

        if not Worker.count(get_connection(RQ_QUEUE_DEFAULT)):
            raise RQWorkerNotRunningException()

        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.finished:
            return Response(
                {"description": f"{obj} is finished, you can't change it."}, status=status.HTTP_400_BAD_REQUEST
            )

        job = obj.enqueue_job(request, "collect_diffs")
        serializer = JobSerializer(job, context={"request": request})
        return Response(serializer.data)


class SubstituteViewSet(NetBoxModelViewSet):
    queryset = Substitute.objects.prefetch_related("platform_setting", "tags")
    serializer_class = SubstituteSerializer
    filterset_class = SubstituteFilterSet
