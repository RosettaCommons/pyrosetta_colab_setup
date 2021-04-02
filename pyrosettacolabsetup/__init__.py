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
