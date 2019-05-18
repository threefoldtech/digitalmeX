from Jumpscale import j

# THIS IS A TEST CHAT


def chat(bot):
    """
    to call http://localhost:5050/chat/session/whoami
    """

    name = bot.string_ask("What is your name?")
    age = bot.int_ask("What is your age? ")
    favorite_langs = bot.multi_choice("Favorite language: ", ["python", "perl", "haskell", "pascal"])
    worst_person = bot.single_choice(
        "Room with stalin, hitler and toby who would you shoot twice? ", ["stalin", "hitler", "toby"]
    )

    R = """
    # You entered
    
    - name is {{name}}
    - age is {{age}}
    - favorite langs {{favorite_langs}}
    - worst person {{worst_person}}

    ### Click next 
    
    for the final step which will redirect you to threefold.me


    """

    R2 = j.tools.jinja2.template_render(text=j.core.text.strip(R), **locals())

    bot.md_show(R2)

    bot.redirect("https://threefold.me")
