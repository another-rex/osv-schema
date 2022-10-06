import os
import subprocess
import asyncio

PATH_TO_APORTS = '/tmp/aports'
PATH_TO_MAIN = 'main'


def do_stuff(output: str, all_versions: list):
    lines = [
        x for x in output.splitlines() if len(x) == 0 or x.startswith('+pkg')
    ]
    lines.reverse()

    current_ver = None
    current_rel = None

    for x in lines:
        if len(x) == 0:
            all_versions.append((current_ver, current_rel))
            continue

        ver = x.split('=')[1]
        if x.startswith('+pkgver'):
            current_ver = ver
            continue

        if x.startswith('+pkgrel'):
            current_rel = ver
            continue


async def more_stuff(dir, dir_to_list):
    routine = asyncio.subprocess.create_subprocess_exec(
        'git',
        'log',
        '--oneline',
        '-L',
        '/pkgver=/,+2:' + os.path.join(dir, 'APKBUILD'),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=dir_to_list)
    stdout_data, stderr_data = (await (await routine).communicate())

    # print(stdout_data)
    # response = subprocess.check_output(['git', 'log', '--oneline', '-L', '/pkgver=/,+2:' + os.path.join(dir, 'APKBUILD')])
    all_versions = []
    do_stuff(stdout_data.decode('utf-8'), all_versions)
    print(all_versions)


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


dir_to_list = os.path.join(PATH_TO_APORTS, PATH_TO_MAIN)
loop = asyncio.get_event_loop()
tasks = []

print(len(os.listdir(dir_to_list)))

for dir in os.listdir(dir_to_list)[:16]:
    # os.chdir(dir_to_list)
    tasks.append(more_stuff(dir, dir_to_list))

    # input()

loop.run_until_complete(
    asyncio.wait([loop.create_task(gather_with_concurrency(4, *tasks))]))
