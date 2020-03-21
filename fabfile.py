from fabric import task
import os


@task
def shell(ctx):
    ctx.run('docker exec -it aplazame_mgc bash', pty=True)


@task
def logs(ctx):
    ctx.run('docker logs --tail 50 -f aplazame_mgc', pty=True)


@task
def down(ctx):
    ctx.run('docker-compose down')


@task
def up(ctx):
    ctx.run('docker-compose up --build -d')


@task
def downup(ctx):
    down(ctx)
    up(ctx)


@task
def manage(ctx, command=None, args='', own_user=True):
    if own_user:
        ctx.run('docker exec -u{} -it aplazame_mgc python3 manage.py {} {}'.format(os.getuid(), command, args), pty=True)
    else:
        ctx.run('docker exec -it aplazame_mgc python3 manage.py {} {}'.format(command, args), pty=True)


@task
def djangoshell(ctx):
    manage(ctx, command='shell', own_user=False)


@task
def createsuperuser(ctx):
    ctx.run('docker exec -it aplazame_mgc python3 manage.py createsuperuser', pty=True)


@task
def makemigrations(ctx):
    ctx.run('docker exec -it aplazame_mgc python3 manage.py makemigrations', pty=True)


@task
def migrate(ctx):
    ctx.run('docker exec -it aplazame_mgc python3 manage.py migrate', pty=True)


@task
def migrations(ctx):
    makemigrations(ctx)
    migrate(ctx)


@task
def postgres(ctx):
    ctx.run('docker exec -it aplazame_postgres bash', pty=True)


@task
def test(ctx):
    manage(ctx, command='test --pattern="test_*.py"', own_user=False)
