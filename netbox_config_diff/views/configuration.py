import django_rq
from core.choices import JobStatusChoices
from core.filtersets import JobFilterSet
from core.forms import JobFilterForm
from core.models import Job
from core.tables import JobTable
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from netbox.constants import RQ_QUEUE_DEFAULT
from netbox.views import generic
from netbox.views.generic.base import BaseObjectView
from rq.exceptions import InvalidJobOperation
from utilities.forms import restrict_form_fields
from utilities.rqworker import get_workers_for_queue
from utilities.utils import normalize_querydict
from utilities.views import ViewTab, register_model_view

from netbox_config_diff.choices import ConfigurationRequestStatusChoices
from netbox_config_diff.filtersets import ConfigurationRequestFilterSet, SubstituteFilterSet
from netbox_config_diff.forms import (
    ConfigurationRequestFilterForm,
    ConfigurationRequestForm,
    ConfigurationRequestScheduleForm,
    SubstituteFilterForm,
    SubstituteForm,
)
from netbox_config_diff.models import ConfigurationRequest, Substitute
from netbox_config_diff.tables import ConfigurationRequestTable, SubstituteTable

from .base import BaseObjectDeleteView, BaseObjectEditView


@register_model_view(ConfigurationRequest)
class ConfigurationRequestView(generic.ObjectView):
    queryset = ConfigurationRequest.objects.all()

    def get_extra_context(self, request, instance):
        job = Job.objects.filter(
            object_id=instance.pk, name__contains="push_configs", status__in=JobStatusChoices.TERMINAL_STATE_CHOICES
        ).first()

        return {
            "job": job,
        }


class ConfigurationRequestListView(generic.ObjectListView):
    queryset = ConfigurationRequest.objects.prefetch_related(
        "devices", "created_by", "approved_by", "scheduled_by", "tags"
    )
    filterset = ConfigurationRequestFilterSet
    filterset_form = ConfigurationRequestFilterForm
    table = ConfigurationRequestTable


@register_model_view(ConfigurationRequest, "edit")
class ConfigurationRequestEditView(BaseObjectEditView):
    queryset = ConfigurationRequest.objects.all()
    form = ConfigurationRequestForm

    def get(self, request, *args, **kwargs):
        obj = self.get_object(**kwargs)
        if obj.finished:
            messages.error(request, f"{obj} is finished, you can't change it.")
            return redirect(obj.get_absolute_url())
        obj = self.alter_object(obj, request, args, kwargs)
        model = self.queryset.model

        initial_data = normalize_querydict(request.GET)
        initial_data["created_by"] = request.user.pk
        form = self.form(instance=obj, initial=initial_data)
        restrict_form_fields(form, request.user)

        return render(
            request,
            self.template_name,
            {
                "model": model,
                "object": obj,
                "form": form,
                "return_url": self.get_return_url(request, obj),
                **self.get_extra_context(request, obj),
            },
        )


@register_model_view(ConfigurationRequest, "delete")
class ConfigurationRequestDeleteView(BaseObjectDeleteView):
    queryset = ConfigurationRequest.objects.all()


@register_model_view(ConfigurationRequest, "diffs")
class ConfigurationRequestDiffsView(generic.ObjectView):
    queryset = ConfigurationRequest.objects.all()
    template_name = "netbox_config_diff/configurationrequest/diffs.html"
    tab = ViewTab(
        label="Diffs",
        permission="netbox_config_diff.view_configurationrequest",
        weight=500,
    )

    def get_extra_context(self, request, instance):
        job = Job.objects.filter(object_id=instance.pk, name__contains="collect_diffs").first()

        return {
            "job": job,
        }


@register_model_view(ConfigurationRequest, "scheduled_job", "scheduled-job")
class ConfigurationRequestScheduledJobView(generic.ObjectChildrenView):
    queryset = ConfigurationRequest.objects.all()
    child_model = Job
    table = JobTable
    template_name = "generic/object_children.html"
    tab = ViewTab(
        label="Scheduled job",
        badge=lambda obj: obj.jobs.filter(
            object_id=obj.pk, name__contains="push_configs", status=JobStatusChoices.STATUS_SCHEDULED
        ).count(),
        permission="netbox_config_diff.view_configurationrequest",
        weight=510,
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return Job.objects.restrict(request.user, "view").filter(
            object_id=parent.pk, name__contains="push_configs", status=JobStatusChoices.STATUS_SCHEDULED
        )

    def get_permitted_actions(self, user, model=None):
        return []

    def get_table(self, data, request, bulk_actions=True):
        table = self.table(data, user=request.user, exclude=("actions",))
        table.configure(request)

        return table


@register_model_view(ConfigurationRequest, "approve")
class ConfigurationRequestApproveView(BaseObjectView):
    queryset = ConfigurationRequest.objects.all()

    def get_required_permission(self):
        return "netbox_config_diff.approve_configurationrequest"

    def get(self, request, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        return redirect(obj.get_absolute_url())

    def post(self, request, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.finished:
            messages.error(request, f"{obj} is finished, you can't change it.")
            return redirect(obj.get_absolute_url())

        if obj.approved_by:
            obj.approved_by = None
            obj.status = ConfigurationRequestStatusChoices.CREATED
            if obj.scheduled:
                obj.scheduled = None
                obj.scheduled_by = None
            messages.success(request, f"Unapproved {obj}")
        else:
            obj.approved_by = User.objects.filter(pk=request.user.pk).first()
            obj.status = ConfigurationRequestStatusChoices.APPROVED
            messages.success(request, f"Approved {obj}")
        obj.save()

        return redirect(obj.get_absolute_url())


@register_model_view(ConfigurationRequest, "schedule")
class ConfigurationRequestScheduleView(BaseObjectEditView):
    queryset = ConfigurationRequest.objects.all()
    form = ConfigurationRequestScheduleForm

    def get_required_permission(self):
        return "netbox_config_diff.approve_configurationrequest"

    def get(self, request, *args, **kwargs):
        obj = self.get_object(**kwargs)
        if obj.finished:
            messages.error(request, f"{obj} is finished, you can't change it.")
            return redirect(obj.get_absolute_url())
        if obj.scheduled:
            messages.error(request, f"{obj} already scheduled.")
            return redirect(obj.get_absolute_url())
        obj = self.alter_object(obj, request, args, kwargs)
        model = self.queryset.model

        initial_data = normalize_querydict(request.GET)
        initial_data["scheduled_by"] = request.user.pk
        initial_data["status"] = ConfigurationRequestStatusChoices.SCHEDULED
        form = self.form(instance=obj, initial=initial_data)
        restrict_form_fields(form, request.user)

        return render(
            request,
            self.template_name,
            {
                "model": model,
                "object": obj,
                "form": form,
                "return_url": self.get_return_url(request, obj),
                **self.get_extra_context(request, obj),
            },
        )

    def post(self, request, pk):
        if not request.user.has_perm("netbox_config_diff.approve_configurationrequest"):
            return HttpResponseForbidden()
        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.finished:
            messages.error(request, f"{obj} is finished, you can't change it.")
        elif not get_workers_for_queue("default"):
            messages.error(request, "Unable to run script: RQ worker process not running.")
        elif obj.scheduled_by:
            messages.error(request, f"{obj} already scheduled.")
        elif obj.approved_by is None:
            messages.error(request, f"Approve {obj} before schedule.")
        else:
            form = self.form(data=request.POST, files=request.FILES, instance=obj)
            if not form.is_valid():
                return render(
                    request,
                    self.template_name,
                    context={
                        "object": obj,
                        "form": form,
                        "return_url": self.get_return_url(request, obj),
                        **self.get_extra_context(request, obj),
                    },
                )
            form.save()
            obj.enqueue_job(request, "push_configs", schedule_at=form.cleaned_data["scheduled"])
            messages.success(request, f"Scheduled job for {obj}")
        return redirect(obj.get_absolute_url())


@register_model_view(ConfigurationRequest, "unschedule")
class ConfigurationRequestUnscheduleView(BaseObjectView):
    queryset = ConfigurationRequest.objects.all()

    def get_required_permission(self):
        return "netbox_config_diff.approve_configurationrequest"

    def get(self, request, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        return redirect(obj.get_absolute_url())

    def post(self, request, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.finished:
            messages.error(request, f"{obj} is finished, you can't change it.")
            return redirect(obj.get_absolute_url())

        if obj.scheduled_by:
            obj.scheduled = None
            obj.scheduled_by = None
            obj.status = ConfigurationRequestStatusChoices.APPROVED
            obj.save()
            queue = django_rq.get_queue(RQ_QUEUE_DEFAULT)
            for result in obj.jobs.filter(name__contains="push_configs", status=JobStatusChoices.STATUS_SCHEDULED):
                result.delete()
                if job := queue.fetch_job(str(result.job_id)):
                    try:
                        job.cancel()
                    except InvalidJobOperation:
                        pass
            messages.success(request, f"Unscheduled {obj}")

        return redirect(obj.get_absolute_url())


@register_model_view(ConfigurationRequest, name="collectdiffs", path="collect-diffs")
class ConfigurationRequestCollectDiffsView(BaseObjectView):
    queryset = ConfigurationRequest.objects.all()

    def get_required_permission(self):
        return "netbox_config_diff.change_configurationrequest"

    def get(self, request, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        return redirect(obj.get_absolute_url())

    def post(self, request, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.finished:
            messages.error(request, f"{obj} is finished, you can't change it.")
        elif not get_workers_for_queue("default"):
            messages.error(request, "Unable to run: RQ worker process not running.")
        else:
            obj.enqueue_job(request, "collect_diffs")
            messages.success(request, f"Start collecting configuration diffs for {obj}")

        return redirect(obj.get_absolute_url())


class JobListView(generic.ObjectListView):
    queryset = Job.objects.filter(Q(name__contains="push_configs") | Q(name__contains="collect_diffs"))
    filterset = JobFilterSet
    filterset_form = JobFilterForm
    table = JobTable
    actions = ("export", "delete", "bulk_delete")


@register_model_view(Substitute)
class SubstituteView(generic.ObjectView):
    queryset = Substitute.objects.all()


class SubstituteListView(generic.ObjectListView):
    queryset = Substitute.objects.prefetch_related("platform_setting", "tags")
    filterset = SubstituteFilterSet
    filterset_form = SubstituteFilterForm
    table = SubstituteTable


@register_model_view(Substitute, "edit")
class SubstituteEditView(BaseObjectEditView):
    queryset = Substitute.objects.all()
    form = SubstituteForm


@register_model_view(Substitute, "delete")
class SubstituteDeleteView(BaseObjectDeleteView):
    queryset = Substitute.objects.all()
