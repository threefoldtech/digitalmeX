from rx import Observable
from Jumpscale import j

import graphene


class Author(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()


class Post(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    author = graphene.Field(Author)


class Query(graphene.ObjectType):
    posts = graphene.List(Post)
    hello = graphene.String(name=graphene.String(default_value="stranger"))

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

    def resolve_count_seconds(root, info, up_to=5):
        return Observable.interval(1000).map(lambda i: "{0}".format(i)).take_while(lambda i: int(i) <= up_to)


schema = graphene.Schema(query=Query, subscription=Subscription)
