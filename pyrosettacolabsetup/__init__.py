# -*- coding: utf-8 -*-
# :noTabs=true:

# (c) Copyright Rosetta Commons Member Institutions.
## @brief  Various scripts for PyRosetta Colab integration 
## @author Kathy Le, Sergey Lyskov


def setup(drivepath='/My Drive', install=None):
  if install is not None: #assuming the user installed the .whl version of PyRosetta
    # Mounting Google Drive and add it to Python sys path  
    google_drive_mount_point = '/content/google_drive'

    import os, sys, time, subprocess
    if os.getenv("DEBUG"): sys.exit(0)

    if 'google.colab' in sys.modules:
      from google.colab import drive
      drive.mount(google_drive_mount_point)

    if not os.getenv("DEBUG"):
      google_drive = google_drive_mount_point + '/My Drive'

    if not os.getenv("DEBUG"):
      # installing PyRosetta
      if sys.version_info.major != 3 or sys.version_info.minor != 7:
        print('Need Python-3.7 to run!')
        sys.exit(1)

      pyrosetta_distr_path = google_drive + '/PyRosetta' 
    
      # finding path to wheel package, if multiple packages is found take first one
      # replace this with `wheel_path = pyrosetta_distr_path + /<wheel-file-name>.whl` if you want to use particular whl file
      wheel_path = pyrosetta_distr_path + '/' + [ f for f in os.listdir(pyrosetta_distr_path) if f.endswith('.whl')][0]
    
      print(f'Using PyRosetta wheel package: {wheel_path}')
 
      subprocess.check_call([sys.executable, '-m', 'pip', 'install', wheel_path])

  else: #assuming the user installed the MinSizeRel version of PyRosetta
    import sys
    is_colab = 'google.colab' in sys.modules
    if is_colab:
      # Mounting Google Drive and add it to Python sys path

      google_drive_mount_point = '/content/google_drive'

      import os, sys, time
      from google.colab import drive
      drive.mount(google_drive_mount_point)
    
      google_drive = google_drive_mount_point + drivepath
      google_drive_prefix = google_drive + '/prefix'

      if not os.path.isdir(google_drive_prefix): os.mkdir(google_drive_prefix)

      pyrosetta_install_prefix_path = '/content/prefix'
      if os.path.islink(pyrosetta_install_prefix_path): os.unlink(pyrosetta_install_prefix_path)
      os.symlink(google_drive_prefix, pyrosetta_install_prefix_path)

      for e in os.listdir(pyrosetta_install_prefix_path): sys.path.append(pyrosetta_install_prefix_path + '/' + e)
      print("Notebook is set for PyRosetta use in Colab.  Have fun!")
    else:
      print("Not in Colab. pyrosettacolabsetup not needed.")

      
 
import os, sys, subprocess, time as time_module

def execute_through_pty(command_line):
    import pty, codecs


    hive, drone = pty.openpty()
    p = subprocess.Popen(command_line, shell=True, stdout=drone, stdin=drone,
                         stderr=subprocess.STDOUT, close_fds=True)

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


def mount_pyrosetta_install(prefix='prefix'):
    if os.getenv("DEBUG"): print('DEBUG mode enable, doing nothing...'); return

    google_drive_mount_point = '/content/google_drive'

    if 'google.colab' in sys.modules:
        from google.colab import drive
        drive.mount(google_drive_mount_point)

    google_drive = google_drive_mount_point + '/MyDrive'
    pyrosetta_install_prefix_path = google_drive + '/' + prefix

    pyrosetta_package_path = pyrosetta_install_prefix_path + f'/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages'
    if pyrosetta_package_path not in sys.path: sys.path.append(pyrosetta_package_path)

    import site
    from importlib import reload
    reload(site)
      
    return pyrosetta_install_prefix_path



def install_pyrosetta(prefix='prefix'):
    if os.getenv("DEBUG"): print('DEBUG mode enable, doing nothing...'); return

    pyrosetta_install_prefix_path = mount_pyrosetta_install(prefix)

    if not os.path.isdir(pyrosetta_install_prefix_path): os.mkdir(pyrosetta_install_prefix_path)

    try:
        import pyrosetta
        print(f'PyRosetta install detected at google-drive/{prefix}... doing noting... (if you want to reinstall PyRosetta please delete {prefix} dir from you GoogleDrive)')
        return
    except ModuleNotFoundError: pass


    print('To obtain PyRosetta license please visit https://www.rosettacommons.org/software/license-and-download')
    login = input('Please enter you RC license login:')
    password  = input('Please enter you RC license password:')

    print('Downloading PyRosetta package...')
    execute_through_pty(f'wget -c --content-disposition --http-user={login} --http-password={password} https://graylab.jhu.edu/download/PyRosetta4/archive/release/PyRosetta4.MinSizeRel.python{sys.version_info.major}{sys.version_info.minor}.ubuntu.wheel/.latest')

    print('Installing PyRosetta...')
    execute_through_pty(f'pip3 install --prefix="{pyrosetta_install_prefix_path}" pyrosetta*.whl')

    import site
    from importlib import reload
    reload(site)

    import pyrosetta
