import os
import sys
import stat
import shutil
import requests
import subprocess
from zipfile import ZipFile


def pycharm_filler(*args, **kwargs):
    return args, kwargs


def del_rw(operation, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)
    pycharm_filler(operation, exc)
    return True
    

class MakeEnv:
    def __init__(self):
        self.build_dir = os.path.join(os.getcwd(), 'build')
        self.dist_dir = os.path.join(os.getcwd(), 'dist')
        self.work_dir = os.path.join(os.getcwd(), 'build', 'work')

    def check_directory(self):
        try:
            if os.path.exists(self.build_dir):
                shutil.rmtree(self.build_dir, onerror=del_rw)
            if os.path.exists(self.dist_dir):
                shutil.rmtree(self.dist_dir, onerror=del_rw)
        except Exception as e:
            print(e.__class__.__name__, e)
            print("Please delete the 'build/' directory, because we aren't able to delete it due to access errors.")
            print("Press any key to try again .  .  .")
            os.system('pause>nul')
            self.check_directory()
            return
        print(sys.version)
        os.mkdir(self.build_dir)
        os.mkdir(self.dist_dir)
        os.mkdir(self.work_dir)


class Build(MakeEnv):
    pyinstaller_version = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True).stdout.strip()

    def __init__(self):
        super().__init__()
        self.is_64_bit = sys.maxsize > 2**32
        self.check_directory()

    def get_pyinstaller(self):
        response = requests.get("https://api.github.com/repos/pyinstaller/pyinstaller/releases/latest")
        latest_version_data = response.json()
        
        pyinstaller_version = latest_version_data['tag_name']

        if self.pyinstaller_version == pyinstaller_version[1:]:
            return

        pyinstaller_url = f"https://github.com/pyinstaller/pyinstaller/archive/refs/tags/{pyinstaller_version}.zip"
        pyinstaller_dir = os.path.join(self.build_dir, 'pyinstaller')
        os.makedirs(pyinstaller_dir, exist_ok=True)
        zip_path = os.path.join(self.build_dir, f"PyInstaller-{pyinstaller_version}.zip")
        pyinstaller = os.path.join(pyinstaller_dir, f"pyinstaller-{pyinstaller_version[1:]}")

        with requests.get(pyinstaller_url, stream=True) as pyinstaller_get:
            pyinstaller_get.raise_for_status()
            with open(os.path.join(self.build_dir, f"PyInstaller-{pyinstaller_version}.zip"), 'wb') as pyinstaller_dest:
                shutil.copyfileobj(pyinstaller_get.raw, pyinstaller_dest)
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(pyinstaller_dir)

        files = os.listdir(pyinstaller)
        for file in files:
            source_path = os.path.join(pyinstaller, file)
            destination_path = os.path.join(pyinstaller_dir, file)
            shutil.move(source_path, destination_path)

        subprocess.run(['pip', 'uninstall', 'pyinstaller', '-y'])
        subprocess.run(['pip', 'install', pyinstaller_dir], cwd=self.build_dir)

    def get_src(self):
        github_qrcode_utility = "https://github.com/srpcd/calculator-tk.git"
        subprocess.run(['git', 'clone', github_qrcode_utility], cwd=self.build_dir)
        shutil.copytree(f"{self.build_dir}\\calculator-tk\\src", os.path.join(self.build_dir, 'src'))
        shutil.rmtree(f"{self.build_dir}\\calculator-tk", onerror=del_rw)
        # subprocess.run(["rmdir", "/Q", "/S", f"{self.build_dir}\\qrcode-utility"])
        # reason I don't use shutil.rmtree is because of access denied due to a readonly issue  # this is fixed!!

    def get_upx(self):
        response = requests.get("https://api.github.com/repos/upx/upx/releases/latest")
        latest_version_data = response.json()
        
        if self.is_64_bit:
            upx_path = latest_version_data['assets'][12]['browser_download_url']
        else:
            upx_path = latest_version_data['assets'][11]['browser_download_url']
        upx_version = latest_version_data['tag_name'][1:]
        # upx_path = f"https://github.com/upx/upx/releases/download/{upx_version}/upx-{upx_version}-win64.zip"

        with requests.get(upx_path, stream=True) as upx_get:
            upx_get.raise_for_status()
            with open(os.path.join(self.build_dir, 'upx.zip'), 'wb') as upx_dest:
                shutil.copyfileobj(upx_get.raw, upx_dest)

        shutil.unpack_archive(os.path.join(self.build_dir, 'upx.zip'), self.build_dir)
        os.rename(os.path.join(self.build_dir, f'upx-{upx_version}-win{"64" if self.is_64_bit else "32"}'),
                  os.path.join(self.build_dir, 'upx'))
        os.remove(os.path.join(self.build_dir, 'upx.zip'))

    def compile(self):
        # self.get_src()
        self.get_pyinstaller()
        self.get_upx()
        command = ['pyinstaller', '--workpath', f'"{self.work_dir}"', '--distpath', f'"{self.dist_dir}"',
                   '--upx-dir', 'build\\upx', '--log-level=DEBUG', '--clean', f'src\\metadata\\main.spec']
        # '--upx-dir', 'build\\upx', '--log-level=DEBUG', '--clean', f'{self.build_dir}\\src\\metadata\\main.spec']
        subprocess.run(' '.join(command))

        return self


if __name__ == '__main__':
    build = Build().compile()
