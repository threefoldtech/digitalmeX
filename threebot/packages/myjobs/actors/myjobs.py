from Jumpscale import j


class myjobs(j.application.ThreeBotActorBase):
    def _init(self, **kwargs):
        self.worker_model = j.servers.myjobs.model_worker
        self.job_model = j.servers.myjobs.model_job

    def list_workers(self, schema_out):
        """
        ```in
        ```

        ```out
        workers = (LO) !jumpscale.myjobs.worker
        ```
        """
        output = schema_out.new()
        for worker in self.worker_model.iterate():
            output.workers.append(worker)

        return output

    def list_jobs(self, schema_out):
        """
        ```in
        ```

        ```out
        jobs = (LO) !jumpscale.myjobs.job
        ```
        """
        output = schema_out.new()
        for job in self.job_model.iterate():
            output.jobs.append(job)

        return output
