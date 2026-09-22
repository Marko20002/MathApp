"""Manage an isolated loopback-only development PostgreSQL cluster.

Requires PostgreSQL executables on PATH and the project Python environment.
Never manages a provider database or another project's cluster.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'data' / 'runtime'
DATA = RUNTIME / 'postgres'
CONFIG = RUNTIME / 'postgres-config.json'


def private_write(path, text):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as stream:
        stream.write(text)


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'start', 'stop', 'status'])
    parser.add_argument('--port', type=int, default=55432, help='Used only at initialization')
    args = parser.parse_args()
    ctl = shutil.which('pg_ctl')
    if not ctl or not shutil.which('initdb'):
        parser.error('Install PostgreSQL and add initdb and pg_ctl to PATH first.')
    if args.action == 'init':
        if CONFIG.exists() or DATA.exists():
            parser.error('Local database already exists. Use start; existing data is never overwritten.')
        env_path = ROOT / 'backend' / '.env'
        if env_path.exists():
            parser.error('backend/.env already exists. Configure PostgreSQL manually; no settings overwritten.')
        if not 1024 <= args.port <= 65535:
            parser.error('Use an unprivileged port between 1024 and 65535.')
        RUNTIME.mkdir(parents=True, exist_ok=True)
        os.chmod(RUNTIME, 0o700)
        config = {'port': args.port, 'password': secrets.token_urlsafe(32)}
        password_file = RUNTIME / 'init-password'
        private_write(password_file, config['password'])
        try:
            run(shutil.which('initdb'), '-D', str(DATA), '-U', 'mathapp', '--encoding=UTF8',
                '--auth-local=scram-sha-256', '--auth-host=scram-sha-256', '--pwfile=' + str(password_file))
        finally:
            password_file.unlink(missing_ok=True)
        private_write(CONFIG, json.dumps(config))
    elif not CONFIG.exists():
        parser.error('Initialize first with: python scripts/local_db.py init')
    config = json.loads(CONFIG.read_text())
    if args.action in ('init', 'start'):
        running = subprocess.run([ctl, '-D', str(DATA), 'status'], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL).returncode == 0
        if not running:
            socket = RUNTIME / 'socket'
            socket.mkdir(exist_ok=True)
            options = f'-h 127.0.0.1 -p {config["port"]} -k "{socket}"'
            run(ctl, '-D', str(DATA), '-l', str(RUNTIME / 'postgres.log'), '-o', options, '-w', 'start')
    elif args.action == 'stop':
        run(ctl, '-D', str(DATA), '-m', 'fast', '-w', 'stop')
    else:
        run(ctl, '-D', str(DATA), 'status')
    if args.action == 'init':
        import psycopg
        with psycopg.connect(host='127.0.0.1', port=config['port'], user='mathapp',
                            password=config['password'], dbname='postgres', autocommit=True) as conn:
            conn.execute('CREATE DATABASE mathapp')
        url = f'postgresql://mathapp:{quote(config["password"], safe="")}@127.0.0.1:{config["port"]}/mathapp'
        private_write(ROOT / 'backend' / '.env', '\n'.join([
            '# LOCAL DEVELOPMENT ONLY. Never commit this file.',
            'DEBUG=True', 'SECRET_KEY=' + secrets.token_urlsafe(48),
            'DATABASE_URL=' + url,
            'ML_MODEL_PATH=models/baseline-v1/classifier.joblib',
            'OPENAI_API_KEY=',
            'OPENAI_MODEL=gpt-5.6-terra',
            'OPENAI_REASONING_EFFORT=medium',
            'OPENAI_MAX_OUTPUT_TOKENS=3500',
            'OPENAI_TIMEOUT_SECONDS=45',
            'ALLOW_PUBLIC_REGISTRATION=true', '',
        ]))
        print('Local PostgreSQL initialized. Connection settings saved privately in backend/.env.')


if __name__ == '__main__':
    main()
