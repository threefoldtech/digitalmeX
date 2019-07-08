from rx import Observable
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
      return 'Hello ' + name

    def resolve_posts(root, info):
        return [
            Post(id=1, title="one", author=Author(id=1, name="Hamdy")),
            Post(id=2, title="two", author=Author(id=2, name="Aly")),
        ]


class RandomType(graphene.ObjectType):
    seconds = graphene.Int()
    random_int = graphene.Int()


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())

    def resolve_count_seconds(root, info, up_to=5):
      return Observable.interval(1000).map(lambda i: "{0}".format(i)).take_while(lambda i: int(i) <= up_to)



schema = graphene.Schema(query=Query, subscription=Subscription)