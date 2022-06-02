# -*- coding: utf-8 -*-
# :noTabs=true:

# (c) Copyright Rosetta Commons Member Institutions.
## @brief  Various scripts for PyRosetta Colab integration
## @author Kathy Le, Sergey Lyskov


import os, os.path, sys, subprocess, shutil, tempfile as tempfile_module, time as time_module

_DEFAULT_PYROSETTA_GOOGLE_DRIVE_INSTALL_PREFIX_ = 'PyRosetta/colab.bin'
_PYROSETTA_EAST_MIRROR_ = 'https://graylab.jhu.edu/download/PyRosetta4/archive/release'
_PYROSETTA_WEST_MIRROR_ = 'https://west.rosettacommons.org/pyrosetta/release/release'
_PYROSETTA_RELEASES_URL_ = _PYROSETTA_WEST_MIRROR_

def execute_through_pty(command_line):
    import pty, codecs
    hive, drone = pty.openpty()
    p = subprocess.Popen(command_line, shell=True, stdout=drone, stdin=drone, stderr=subprocess.STDOUT, close_fds=True)

    os.close(drone)

    buffer = []
    to_print = b''
    while True:
        try:
            data = b''
            while True:
                c = os.read(hive, 1)
                data += c
                if c not in codecs.BOM_UTF8: break

            if data:
                buffer.append(data)

                to_print += data

                if to_print:
                    for b in b'\r\n':
                        if b == to_print[-1]:
                            print(to_print[:-1].decode(encoding='utf-8', errors='backslashreplace'), end='')
                            to_print = to_print[-1:]
                            break

        except OSError: break  # OSError will be raised when child process close PTY descriptior

    output = b''.join(buffer).decode(encoding='utf-8', errors='backslashreplace')

    os.close(hive)

    p.wait()
    exit_code = p.returncode

    return exit_code, output


def check_for_rosetta_so_file(prefix, pyrosetta_package_path):
    rosetta_so_path = pyrosetta_package_path + f'/pyrosetta/rosetta.so'
    if os.path.isfile(rosetta_so_path):
        print(f'PyRosetta installed at {prefix!r}... Please click "Runtime → Restart runtime" before using it.')
        return False
    else:
        print(f'ERROR ERROR ERROR: looks PyRosetta like install procedure has not worked correctly!!!\nERROR ERROR ERROR: Please remove dir {prefix!r} from your Google Drive and then re-run install procedure again!\n\n')
        return True


def mount_google_drive():
    if os.getenv("DEBUG"): print('DEBUG mode enable, doing nothing...'); return

    google_drive_mount_point = '/content/google_drive'

    #if 'google.colab' in sys.modules:
    from google.colab import drive
    drive.mount(google_drive_mount_point)

    google_drive_path = google_drive_mount_point + '/MyDrive'

    return google_drive_path



def mount_pyrosetta_google_drive_install(prefix=_DEFAULT_PYROSETTA_GOOGLE_DRIVE_INSTALL_PREFIX_, suppres_rosetta_so_check=False):
    if os.getenv("DEBUG"): print('DEBUG mode enable, doing nothing...'); return

    pyrosetta_install_prefix_path = mount_google_drive() + '/' + prefix

    pyrosetta_package_path = pyrosetta_install_prefix_path + f'/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages'
    if pyrosetta_package_path not in sys.path: sys.path.append(pyrosetta_package_path)

    import site
    from importlib import reload
    reload(site)

    if not suppres_rosetta_so_check: check_for_rosetta_so_file(prefix, pyrosetta_package_path)

    return pyrosetta_install_prefix_path, pyrosetta_package_path


def download_pyrosetta_wheel(prefix, location):
    ''' download appropriate PyRosetta wheel package to specified `location` and return path to it
        while making sure that partial download is not appear at target location
    '''
    print('To obtain PyRosetta license please visit https://www.rosettacommons.org/software/license-and-download')
    login = input('Please enter you RC license login:')
    password  = input('Please enter you RC license password:')

    with tempfile_module.TemporaryDirectory(dir=prefix) as tmpdirname:
        print('Downloading PyRosetta package...')
        execute_through_pty(f'wget --directory-prefix={tmpdirname} -c --content-disposition --http-user={login} --http-password={password} {_PYROSETTA_RELEASES_URL_}/PyRosetta4.MinSizeRel.python{sys.version_info.major}{sys.version_info.minor}.ubuntu.wheel/.latest')
        for f in os.listdir(tmpdirname):
            if f.startswith('pyrosetta-') and f.endswith('.whl'):
                if not os.path.isdir(location): os.makedirs(location)
                print(f'Moving wheel file {f} to target dir {location}...')
                shutil.move(f'{tmpdirname}/{f}', f'{location}/{f}')
                return(f'{location}/{f}')

        print('ERROR: Wheel download has not worked correctly, ABORTING...')
        sys.exit(1)


def install_pyrosetta_on_google_drive(prefix=_DEFAULT_PYROSETTA_GOOGLE_DRIVE_INSTALL_PREFIX_):
    if os.getenv("DEBUG"): print('DEBUG mode enable, doing nothing...'); return

    pyrosetta_install_prefix_path, pyrosetta_package_path = mount_pyrosetta_google_drive_install(prefix, suppres_rosetta_so_check=True)

    if not os.path.isdir(pyrosetta_install_prefix_path): os.makedirs(pyrosetta_install_prefix_path)

    try:
        import pyrosetta
        print(f'PyRosetta install detected at google-drive/{prefix}... doing noting... (if you want to reinstall PyRosetta please delete {prefix} dir from you GoogleDrive)')
        return
    except ModuleNotFoundError: pass

    wheel_path = download_pyrosetta_wheel(pyrosetta_install_prefix_path, pyrosetta_install_prefix_path + '/wheels')

    print(f'Installing PyRosetta wheel {wheel_path!r}...')
    execute_through_pty(f'pip3 install --prefix="{pyrosetta_install_prefix_path}" {wheel_path}')

    if pyrosetta_package_path not in sys.path: sys.path.append(pyrosetta_package_path)

    import site
    from importlib import reload
    reload(site)

    if check_for_rosetta_so_file(prefix, pyrosetta_package_path): sys.exit(1)

    # import main PyRosetta module by-hands so we can avoid doing Colab runtime restart
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("pyrosetta", f'{pyrosetta_package_path}/pyrosetta/__init__.py')
    pyrosetta = loader.load_module("pyrosetta")


def install_pyrosetta_on_colab(prefix=_DEFAULT_PYROSETTA_GOOGLE_DRIVE_INSTALL_PREFIX_, cache_wheel_on_google_drive=True):

    try:
        import pyrosetta
        return
    except ModuleNotFoundError: pass

    if cache_wheel_on_google_drive: pyrosetta_root = mount_google_drive() + '/' + prefix
    else:
      pyrosetta_root = '/' + prefix
      os.makedirs(pyrosetta_root)

    if cache_wheel_on_google_drive: pyrosetta_wheels_path = pyrosetta_root + '/wheels'
    else: pyrosetta_wheels_path = pyrosetta_root + '/wheels'

    # see if PyRosetta wheel is already downloaded...
    print(f'Looking for compatible PyRosetta wheel file at google-drive/{prefix}/wheels...')
    if os.path.isdir(pyrosetta_wheels_path):
        wheels = [ f for f in os.listdir(pyrosetta_wheels_path) if f.startswith('pyrosetta-2') and f.endswith('.whl') and f'-cp{sys.version_info.major}{sys.version_info.minor}-' in f]
    else: wheels = []

    if wheels:
        wheel = pyrosetta_wheels_path + '/' + sorted(wheels)[-1]
        print(f'Found compatible wheel: {pyrosetta_wheels_path}/{wheel}')
    else:
        wheel = download_pyrosetta_wheel(pyrosetta_root, pyrosetta_wheels_path)
        print(f'Installing PyRosetta wheel {wheel!r}...')

    execute_through_pty(f'pip3 install {wheel}')
    import pyrosetta


install_pyrosetta = mount_pyrosetta_install = install_pyrosetta_on_colab
