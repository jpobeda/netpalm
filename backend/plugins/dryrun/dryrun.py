from backend.plugins.napalm.napalm_drvr import naplm
from backend.plugins.ncclient.ncclient_drvr import ncclien
from backend.plugins.jinja2.j2 import render_j2template

from backend.plugins.webhook.webhook import exec_webhook_func
from backend.core.meta.rediz_meta import prepare_netpalm_payload

def dryrun(**kwargs):
    lib = kwargs.get("library", False)
    config = kwargs.get("config", False)
    j2conf =  kwargs.get("j2config", False)
    webhook = kwargs.get("webhook", False)

    if j2conf:
        j2confargs = j2conf.get("args")
        try:
            res = render_j2template(j2conf["template"], kwargs=j2confargs)
            config = res["data"]["task_result"]["template_render_result"]
        except Exception as e:
            config = False
            return e
    try:
        result = {}
        if lib == "napalm":
            napl = naplm(**kwargs)
            sesh = napl.connect()
            result = napl.config(session=sesh,command=config,dry_run=True)
            napl.logout(sesh)
        elif lib == "ncclient":
            ncc = ncclien(**kwargs)
            sesh = ncc.connect()
            result = ncc.editconfig(session=sesh,dry_run=True)
            ncc.logout(sesh)
        if webhook:
            current_jobdata = prepare_netpalm_payload(job_result=result)
            exec_webhook_func(jobdata=current_jobdata, webhook_payload=webhook)
        return result
    except Exception as e:
        return str(e)