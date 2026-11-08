import subprocess, os, time, signal

prompt = '/Users/Ori/Documents/Projects/BunkerGame/.director/runs/warehouse-meshid-fix-02-da55022b4844.prompt.txt'
env = os.environ.copy()
env.pop('FORCE_NO_TTY', None)
logf = open('/tmp/cn_exact2.out', 'w')
pin = open(prompt, 'r')
proc = subprocess.Popen(
    ['/Users/Ori/.npm-global/bin/cn', '-p', '--config', '/Users/Ori/.continue/config.yaml', '--auto', '--silent'],
    cwd='/Users/Ori/Documents/Projects/BunkerGame',
    env=env,
    stdin=pin,
    stdout=logf,
    stderr=subprocess.STDOUT,
    start_new_session=True,
    text=True,
)
pin.close()
time.sleep(45)
if proc.poll() is None:
    print('STILL_RUNNING after 45s, pid', proc.pid)
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except Exception as e:
        print('kill', e)
    try:
        proc.wait(timeout=10)
    except Exception:
        pass
else:
    print('EXITED rc=', proc.returncode)
logf.close()
print('---OUT tail---')
print(open('/tmp/cn_exact2.out').read()[-1500:])