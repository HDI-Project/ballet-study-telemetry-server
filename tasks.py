from invoke import task


@task
def test(c):
    c.run('python -m pytest -v', pty=True)


@task
def lint(c):
    c.run('flake8 bsts tests')


@task
def serve(c):
    c.run('honcho start', pty=True)


@task
def push_env(c, file='.env'):
    """Push .env key/value pairs to heroku"""
    redlist = ('DATABASE_URL', )
    from honcho.environ import parse
    with open(file, 'r') as f:
        env = parse(f.read())
    cmd = 'heroku config:set ' + ' '.join(
        f'{key}=\'{value}\''
        for key, value in env.items()
        if key not in redlist
    )
    c.run(cmd)


@task
def deploy(c):
    c.run('git push heroku master')
