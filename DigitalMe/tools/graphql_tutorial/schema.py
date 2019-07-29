

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


from Jumpscale import j
import random
import asyncio
import graphene


class Author(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()


class Post(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    author = graphene.Field(Author)


class Query(graphene.ObjectType, j.application.JSBaseConfigsClass):
    posts = graphene.List(Post)

    def resolve_posts(self, root):
        _SCHEMA_TEXT = """
        @url = graphql.info.schema
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
    random_int = graphene.Field(RandomType)

    async def resolve_count_seconds(root, info, up_to=500):
        for i in range(up_to):
            print("YIELD SECOND", i)
            yield i
            await asyncio.sleep(1.0)
        yield up_to

    async def resolve_random_int(root, info):
        i = 0
        while True:
            yield RandomType(seconds=i, random_int=random.randint(0, 500))
            await asyncio.sleep(1.0)
            i += 1


schema = graphene.Schema(query=Query, subscription=Subscription)
