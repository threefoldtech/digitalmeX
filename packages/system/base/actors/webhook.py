from Jumpscale import j


class webhook(j.application.JSBaseClass):
    def pull_repo(self, url, name):
        """
        ```in
        url = ""
        name = ""
        ```
        :param url: git url of the repository you need to pull
        :return:
        """
        j.clients.git.pullGitRepo(url)
        threefold_docsite = j.tools.markdowndocs.load(url, name=name)
        threefold_docsite.write()
        return True
