from Jumpscale import j


class webhook(j.application.JSBaseClass):
    def pull_repo(self, url, name, docs_path):
        """
        ```in
        url = ""
        name = ""
        docs_path = ""
        ```
        :param url: git url of the repository you need to pull
        :return:
        """
        j.clients.git.pullGitRepo(url)
        if name and docs_path:
            threefold_docsite = j.tools.markdowndocs.load(docs_path, name=name)
            threefold_docsite.write()
        return True
