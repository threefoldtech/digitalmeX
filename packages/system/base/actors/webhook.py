from Jumpscale import j


class webhook(j.application.JSBaseClass):
    def pull_repo(self, url):
        """
        ```in
        url = ""
        ```
        :param url: git url of the repository you need to pull
        :return:
        """
        j.clients.git.pullGitRepo(url)
        return True
