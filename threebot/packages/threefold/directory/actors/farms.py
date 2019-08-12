from Jumpscale import j


class farms(j.application.ThreeBotActorBase):
    def _init(self, **kwargs):
        bcdb = j.data.bcdb.get("tf_directory")
        self.farm_model = bcdb.model_get_from_url("tfgrid.farm.1")

    def register(self, farm):
        """
        ```in
        farm = (O) !tfgrid.farm.1
        ```
        """
        self.farm_model.set(farm)
        return True

    # do we need this or can we abuse register ?
    # def update(self, farm):
    #     pass

    def get(self, farm_id, schema_out):
        """
        ```in
        farm_id = (S)
        ```

        ```out
        farm = (O) !tfgrid.farm.1
        ```
        """
        farms = self.farm_model.find(farm_id=farm_id)
        if len(farms) <= 0:
            raise j.exceptions.NotFound("node %s not found" % farm_id)

        return farms[0]

    def list(self, farm, country, city, schema_out):
        """
        ```in
        farm = (S)
        country = (S)
        city = (S)
        ```

        ```out
        farms = (LO) !tfgrid.farm.1
        ```
        """
        output = schema_out.new()

        for farm in self.farm_model.iterate():
            if country != "" and farm.country != country:
                continue
            if city != "" and farm.city != city:
                continue
            output.farms.append(farm)

        return output
