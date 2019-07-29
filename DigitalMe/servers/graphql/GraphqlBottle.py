

# Copyright (C) 2019 :  TF TECH NV in Belgium see https://www.threefold.tech/
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.


import json
from collections import namedtuple

from bottle import request, response

from graphql import GraphQLError, format_error as format_graphql_error


def format_error(error):
    if isinstance(error, GraphQLError):
        return format_graphql_error(error)

    return {"message": str(error)}


def handle_graphql_response(func, graphene_schema):
    def wrapper():
        response.content_type = "application/json"

        try:
            result = func(graphene_schema)
            output = {"data": result.data}

            if result.errors is not None:
                output["errors"] = [format_error(e) for e in result.errors]

            if result.invalid:
                response.status = 400

            return json.dumps(output)
        except Exception as e:
            return json.dumps({"data": None, "errors": [e]})

    return wrapper


def execute_get(graphene_schema):
    graphql_query = request.query["query"]
    graphql_variables = json.loads(request.query.get("variables", "{}"))
    graphql_operation_name = request.query.get("operationName", None)

    return graphene_schema.execute(
        graphql_query, variable_values=graphql_variables, operation_name=graphql_operation_name
    )


def execute_post(graphene_schema):
    graphql_data = request.json
    graphql_query = graphql_data["query"]

    return graphene_schema.execute(graphql_query)


def execute_introspection(graphene_schema):
    DataItem = namedtuple("DataItem", ["data", "errors"])
    return DataItem(data=graphene_schema.introspect(), errors=None)


def graphql_middleware(bottle_app, endpoint_name, graphene_schema):
    bottle_app.route(endpoint_name, "OPTIONS", handle_graphql_response(execute_introspection, graphene_schema))
    bottle_app.route(endpoint_name, "POST", handle_graphql_response(execute_post, graphene_schema))
    bottle_app.route(endpoint_name, "GET", handle_graphql_response(execute_get, graphene_schema))
