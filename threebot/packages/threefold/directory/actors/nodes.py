from Jumpscale import j


class nodes(j.application.ThreeBotActorBase):
    def _init(self, **kwargs):
        bcdb = j.data.bcdb.get("tf_directory")
        self.node_model = bcdb.model_get_from_url("tfgrid.node.1")

    def add(self, node):
        """
        ```in
        !tfgrid.node.1
        ```
        """
        # TODO check the sender is actually the node itself
        # TODO: first check of the node already exist and if so do an update ?

        # FIXME: we should not have to use _ddict since node is already a JSX object
        node = self.node_model.new(node._ddict)
        node.save()

        return node._key  # not sure about this _key ?

    def list(self, farm, country, city, cru, sru, mru, hru, schema_out):
        """
        ```in
        farm = (S)
        country = (S)
        city = (S)
        cru = -1 (I)
        mru = -1 (I)
        sru = -1 (I)
        hru = -1 (I)
        ```

        ```out
        nodes = (LO) !tfgrid.node.1
        ```
        """
        output = schema_out.new()

        for node in self.node_model.iterate():
            if country != "" and node.country != country:
                continue
            if city != "" and node.city != city:
                continue
            if cru > -1 and node.cru < cru:
                continue
            if mru > -1 and node.mru < mru:
                continue
            if sru > -1 and node.sru < sru:
                continue
            if hru > -1 and node.hru < hru:
                continue
            output.nodes.append(node)

        return output

    def get(self, node_id, schema_out):
        """
        ```in
        node_id = (S)
        ```

        ```out
        node = (O) !tfgrid.node.1
        ```
        """
        nodes = self.node_model.find(node_id=node_id)
        if len(nodes) <= 0:
            # raise RuntimeError("not found")
            raise j.exceptions.NotFound("node %s not found" % node_id)

        return nodes[0]
