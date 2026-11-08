import subprocess, os, time, signal

prompt = '/Users/Ori/Documents/Projects/BunkerGame/.director/runs/warehouse-meshid-fix-02-da55022b4844.prompt.txt'
env = os.environ.copy()
env.pop('FORCE_NO_TTY', None)

def run(label, use_file_stdin, use_setsid, seconds=25):
    logf = open(f'/tmp/cn_iso_{label}.out', 'w')
    if use_file_stdin:
        pin = open(prompt, 'r')
    else:
        pin = subprocess.PIPE
    kw = dict(cwd='/Users/Ori/Documents/Projects/BunkerGame', env=env, stdout=logf, stderr=subprocess.STDOUT, text=True)
    if use_setsid:
        kw['start_new_session'] = True
    proc = subprocess.Popen(['/Users/Ori/.npm-global/bin/cn','-p','--config','/Users/Ori/.continue/config.yaml','--auto','--silent'], stdin=pin, **kw)
    if not use_file_stdin:
        proc.stdin.write(open(prompt).read())
        proc.stdin.close()
    else:
        pin.close()
    time.sleep(seconds)
    if proc.poll() is None:
        print(f'{label}: STILL_RUNNING after {seconds}s')
        try:
            if use_setsid:
                os.killpg(proc.pid, signal.SIGTERM)
            else:
                proc.terminate()
        except Exception as e:
            print(f'{label}: kill err {e}')
        try:
            proc.wait(timeout=8)
        except Exception:
            pass
    else:
        print(f'{label}: EXITED rc={proc.returncode}')
    logf.close()
    out = open(f'/tmp/cn_iso_{label}.out').read()
    print(f'{label}: OUTLEN={len(out)} tail={out[-200:]!r}')

# A: file stdin, NO setsid
run('A_file_nosetsid', True, False)
# B: pipe stdin, WITH setsid
run('B_pipe_setsid', False, True)