import re
import os
import subprocess
import sys
from pathlib import Path

RELYZE_INSTALL = Path(os.getenv("RELYZE_INSTALL_PATH", "/home/decompiler_user/RelyzeDesktop/app"))
RELYZE_CLI     = RELYZE_INSTALL / 'RelyzeCLI.exe'
RELYZE_PLUGIN  = Path(__file__).resolve().parent / 'decompiler_explorer.rb'

def relyze_cli_run(params):
    if not RELYZE_CLI.is_file():
        return False, f'\'{RELYZE_CLI.name}\' not found.'

    cwd = Path.cwd()
    logfile = cwd / 'log.tmp'

    cli = subprocess.run(['wine64', str(RELYZE_CLI), '/output', logfile.name] + params, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=cwd)

    logdata = ''

    if logfile.is_file():
        with open(logfile, 'r', encoding='utf-16-le') as f:
            logdata = f.read()
        logfile.unlink()

    if cli.returncode != 0:
        return False, f'{logdata}\n{cli.stdout.decode()}'

    return True, logdata

def main():

    cwd = Path.cwd()
    infile  = cwd / 'in.tmp'
    outfile = cwd / 'out.tmp'

    with open(infile, 'wb') as f:
        f.write(sys.stdin.buffer.read())

    func_timeout = int(os.getenv('DECOMPILER_FUNC_TIMEOUT', 15))

    success, res = relyze_cli_run([
        '/run',
        '/plugin',
        str(RELYZE_PLUGIN),
        '/plugin_commandline',
        f'/in={infile.name} /out={outfile.name} /func_timeout={func_timeout}'
    ])

    infile.unlink()

    if not success:
        print(res)
        if outfile.is_file():
            outfile.unlink()
        return 1

    if outfile.is_file():
        with open(outfile, 'r') as f:
            print(f.read())
        outfile.unlink()
    else:
        print('no output file.')
        return 1

    return 0

def version():
    success, ver = relyze_cli_run(['/version'])
    if not success:
        return 1
    match = re.findall(r'\s(\d+\.\d+\.\d+)\s', ver)
    if len(match) == 0:
        return 1
    print(match[0])
    print()
    return 0

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--name':
        print('Relyze')
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == '--url':
        print('https://www.relyze.com/')
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == '--version':
        sys.exit(version())

    sys.exit(main())
