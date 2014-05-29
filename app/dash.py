import cherrypy, simplejson, hmac, hashlib, os, subprocess
from pwd import getpwnam

class Dash(object):
    @cherrypy.expose
    def index(self):
        if (cherrypy.request.headers['X-Github-Event'] != 'push'):
            return "can't handle this event"

        payload = simplejson.loads(self.get_body())

        repo_name = '{0}/{1}'.format(payload['repository']['owner']['name'], payload['repository']['name'])
        repo_config = self.get_repository_config(repo_name)

        if (repo_config == None):
            return "no config for {0}".format(repo_name)

        # Make sure the signature is valid
        if (not self.validate_signature(repo_config['secret'])):
            return "secret mismatch"

        # Check branch
        ref = payload['ref']
        if (ref[0:11] != 'refs/heads/'):
            return "not on branch"

        branch_name = payload['ref'][11:]
        if (branch_name not in repo_config['branches']):
            return "no config for branch {0}".format(branch_name)

        branch_config = repo_config['branches'][branch_name]

        def my_preexec_fn():
            os.chdir(branch_config['directory'])
            try:
                os.setuid(getpwnam(branch_config['user']).pw_uid)
            except:
                pass

        proc = subprocess.Popen(['git', 'pull', 'origin', branch_name],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=my_preexec_fn)
        out, err = proc.communicate()

        if out:
            print out

        if err:
            print "!! Err !!"
            print err

        if 'after' in branch_config:
            for command in branch_config['after']:
                proc = subprocess.Popen(command ,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=my_preexec_fn)
                out, err = proc.communicate()

                if out:
                    print out

                if err:
                    print "!! Err !!"
                    print err

        return "thanks"

    def get_config(self):
        filecontents = None
        with open("config.json") as f:
            filecontents = simplejson.load(f)
        return filecontents

    def get_repository_config(self, repo):
        config = self.get_config()
        if repo in config['repositories']:
            return config['repositories'][repo]
        else:
            return None

    def validate_signature(self, secret):
        rawsig = cherrypy.request.headers['X-Hub-Signature']
        (algo,sig) = rawsig.split('=', 1)
        expected_sig = hmac.new('test', self.get_body(), hashlib.sha1).hexdigest()
        return (expected_sig == sig)

    def get_body(self):
        if (not hasattr(self, 'body')):
            cl = cherrypy.request.headers['Content-Length']
            self.body = cherrypy.request.body.read(int(cl))
        return self.body

cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 7053
cherrypy.quickstart(Dash())