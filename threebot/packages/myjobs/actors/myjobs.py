from Jumpscale import j


WORKERS = """
{
"workers": [
{
"timeout": "3,600",
"time_start": "2019/08/21 15:57:51",
"last_update": "2019/08/21 16:10:03",
"current_job": "-",
"error": "",
"state": "NEW",
"pid": "0",
"halt": false,
"id": 1
},
{
"timeout": "3,600",
"time_start": "2019/08/21 15:57:54",
"last_update": "2019/08/21 15:57:54",
"current_job": "-",
"error": "",
"state": "new",
"pid": "0",
"halt": false,
"id": 2
},
{
"timeout": "3,600",
"time_start": "2019/08/21 15:57:56",
"last_update": "2019/08/21 16:03:42",
"current_job": "-",
"error": "",
"state": "NEW",
"pid": "0",
"halt": false,
"id": 3
}
]
}
"""


JOBS = """
{
"jobs": [
{
"category": "",
"time_start": "2019/08/21 16:01:41",
"time_stop": "2019/08/21 16:01:41",
"state": "OK",
"timeout": "0",
"action_id": "4",
"args": [1,2],
"kwargs": "{}",
"result": "3",
"error": "{}",
"return_queues": [],
"id": 5
},
{
"category": "",
"time_start": "2019/08/21 16:03:42",
"time_stop": "2019/08/21 16:05:22",
"state": "OK",
"timeout": "0",
"action_id": "6",
"args": [1,2],
"kwargs": "{}",
"result": "3",
"error": "{}",
"return_queues": [],
"id": 7
},
{
"category": "",
"time_start": "2019/08/21 16:10:03",
"time_stop": "2019/08/21 16:11:43",
"state": "OK",
"timeout": "0",
"action_id": "6",
"args": [1,2],
"kwargs": "{}",
"result": "3",
"error": "{}",
"return_queues": [],
"id": 8
}
]
}
"""


class myjobs(j.application.ThreeBotActorBase):
    def _init(self, **kwargs):
        self.worker_model = j.servers.myjobs.model_worker
        self.job_model = j.servers.myjobs.model_job
        self.action_model = j.servers.myjobs.model_action

    # def list_workers(self, schema_out):
    #     """
    #     ```in
    #     ```

    #     ```out
    #     workers = (LO) !jumpscale.myjobs.worker
    #     ```
    #     """
    #     out = schema_out.new()
    #     out.workers = list(self.worker_model.iterate())
    #     return out

    # def list_jobs(self, schema_out):
    #     """
    #     ```in
    #     ```

    #     ```out
    #     jobs = (LO) !jumpscale.myjobs.job
    #     ```
    #     """
    #     out = schema_out.new()
    #     out.jobs = list(self.job_model.iterate())
    #     return out

    # def list_actions(self, schema_out):
    #     """
    #     ```in
    #     ```

    #     ```out
    #     actions = (LO) !jumpscale.myjobs.action
    #     ```
    #     """
    #     out = schema_out.new()
    #     out.actions = list(self.action_model.iterate())
    #     return out

    def list_workers(self):
        return WORKERS

    def list_action(self):
        return []

    def list_jobs(self):
        return JOBS
