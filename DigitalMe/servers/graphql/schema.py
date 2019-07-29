

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


from rx import Observable, Observer
from Jumpscale import j

import graphene


class Author(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()


class Post(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    author = graphene.Field(Author)


class Article(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    author = graphene.Field(Author)


class CreateAuthor(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    ok = graphene.Boolean()
    author = graphene.Field(lambda: Author)
    affected_rows = graphene.Int()

    def mutate(root, info, **kwargs):
        _SCHEMA_TEXT = """
                       @url = graphql.authors.schema
                       name = (S)
                       """
        model = j.application.bcdb_system.model_get_from_schema(_SCHEMA_TEXT)
        model_objects = model.new()
        model_objects.name = kwargs["name"]
        model_objects.save()

        ok = True
        affected_rows = 1
        author = Author(name=kwargs["name"], id=model_objects.id)
        return CreateAuthor(author=author, ok=ok, affected_rows=affected_rows)


class Mutations(graphene.ObjectType):
    create_author = CreateAuthor.Field()


class Query(graphene.ObjectType):
    posts = graphene.List(Post)
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    author = graphene.List(Author)
    article = graphene.List(Article)

    def resolve_article(self, info):
        return [Article(id=1, title="article1", author=Author(id=1, name="author1"))]

    def resolve_author(self, info):
        _SCHEMA_TEXT = """
                @url = graphql.authors.schema
                name = (S)
                """
        model = j.application.bcdb_system.model_get_from_schema(_SCHEMA_TEXT)

        results = []
        for item in model.iterate():
            results.append({"id:": item.id, "name": item.name})
        return results

    def resolve_hello(self, info, name):
        return "Hello " + name

    # get data from bcdb
    def resolve_posts(root, info):
        _SCHEMA_TEXT = """
        @url = graphql.posts.schema
        info_id* = (I)
        title = (S) 
        author = (S)
        name = (S)
        """
        model = j.application.bcdb_system.model_get_from_schema(_SCHEMA_TEXT)

        results = []
        for item in model.iterate():
            results.append(Post(id=item.id, title=item.title, author=Author(id=item.id, name=item.name)))
        return results


class RandomType(graphene.ObjectType):
    seconds = graphene.Int()
    random_int = graphene.Int()


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())
    author = graphene.List(Author)

    def resolve_count_seconds(root, info, up_to=5):
        return Observable.interval(1000).map(lambda i: "{0}".format(i)).take_while(lambda i: int(i) <= up_to)

    def resolve_author(root, info):
        import json

        authors = [Author(id=1, name="a"), Author(id=2, name="b")]

        class PrintObserver(Observer):
            def on_next(self, value):
                pass

            def on_completed(self):
                pass

            def on_error(self, error):
                pass

        source = Observable.from_list(authors)
        source.subscribe(PrintObserver())
        return source


schema = graphene.Schema(query=Query, subscription=Subscription, mutation=Mutations)
