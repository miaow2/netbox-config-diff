import logging
import traceback

from core.choices import JobStatusChoices
from core.models import Job
from utilities.utils import NetBoxFakeRequest

from netbox_config_diff.choices import ConfigurationRequestStatusChoices
from netbox_config_diff.configurator.base import Configurator
from netbox_config_diff.models import ConfigurationRequest

logger = logging.getLogger(__name__)


def collect_diffs(job: Job, request: NetBoxFakeRequest, *args, **kwargs) -> None:
    job.start()
    cr = ConfigurationRequest.objects.get(pk=job.object_id)
    logger.info(f"Collecting diffs for {cr}")
    configurator = Configurator(cr.devices.all(), request)
    try:
        configurator.validate_devices()
        configurator.collect_diffs()
        job.data = configurator.logger.get_data()
        job.terminate()
    except Exception as e:
        stacktrace = traceback.format_exc()
        configurator.logger.log_failure(f"An exception occurred: `{type(e).__name__}: {e}`\n```\n{stacktrace}\n```")
        logger.error(f"Exception raised during script execution: {e}")
        job.data = configurator.logger.get_data()
        job.terminate(status=JobStatusChoices.STATUS_ERRORED)

    logger.info(f"Collecting diffs job completed in {job.duration}")


def push_configs(job: Job, request: NetBoxFakeRequest, *args, **kwargs) -> None:
    cr = ConfigurationRequest.objects.get(pk=job.object_id)
    cr.start(job)
    logger.info(f"Applying configs for {cr}")
    configurator = Configurator(cr.devices.all(), request)
    try:
        configurator.validate_devices()
        configurator.push_configs()
        job.data = configurator.logger.get_data()
        cr.terminate(job=job)
    except Exception as e:
        stacktrace = traceback.format_exc()
        configurator.logger.log_failure(f"An exception occurred: `{type(e).__name__}: {e}`\n```\n{stacktrace}\n```")
        logger.error(f"Exception raised during script execution: {e}")
        job.data = configurator.logger.get_data()
        cr.terminate(job=job, status=ConfigurationRequestStatusChoices.ERRORED)

    logger.info(f"Applying configs job completed in {job.duration}")
