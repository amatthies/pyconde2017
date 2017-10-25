import json
import logging
import os
import shutil
import tempfile
import time
import zipfile
from pathlib import Path

import requests
import yaml
from pkg_resources import resource_string, resource_filename
from tqdm import tqdm

logger = logging.getLogger(__name__)

ZIP_EXCLUDES = [
    '*.exe', '*.DS_Store', '*.Python', '*.git', '.git/*', '*.zip', '*.tar.gz',
    '*.hg', '*.egg-info', 'pip', 'docutils*', 'setuputils*', '__pycache__*', '__pycache__/*']


def contains_python_files_or_subdirs(folder):
    """
    Checks (recursively) if the directory contains .py or .pyc files
    """
    fp = Path(folder)
    for _ in fp.glob('**/*.py'):
        return True

    for _ in fp.glob('**/*.pyc'):
        return True


def conflicts_with_a_neighbouring_module(directory_path):
    """
    Checks if a directory lies in the same directory as a .py file with the same name.
    """
    current_dir = Path(directory_path)
    conflicting_neighbours = list(current_dir.parent.glob(current_dir.name + '.py'))

    return len(conflicting_neighbours) > 0


class LambdaZipper:
    def __init__(self, lambda_name: str, target_dir: str = 'dist_lambda', output: str = None):
        """

        Parameters
        ----------
        lambda_name
            The directory, where the lambda is stored. Will be used as name
        """
        self.lambda_name = lambda_name
        self.config = yaml.load(resource_string('lambdas', f'{self.lambda_name}/config.yml'))
        self.wheels = json.loads(resource_string('lambdas', 'wheels.json'))
        self.project_dir = Path(resource_filename('lambdas', lambda_name))
        self.package_dir = Path(target_dir)
        zip_fname = output or lambda_name + '-' + str(int(time.time())) + '.zip'
        self.zip_path = Path(self.package_dir, zip_fname)
        self.exclude = [
            "boto3",
            "dateutil",
            "botocore",
            "s3transfer",
            "concurrent",
            str(self.zip_path)
        ]

    @staticmethod
    def compression_method():
        try:
            # noinspection PyUnresolvedReferences
            import zlib
        except ImportError:
            return zipfile.ZIP_STORED
        else:
            return zipfile.ZIP_DEFLATED

    def package(self):

        temp_project_path = Path(tempfile.gettempdir(), str(int(time.time())))
        shutil.copytree(str(self.project_dir), str(temp_project_path),
                        symlinks=False, ignore=shutil.ignore_patterns(*ZIP_EXCLUDES, *self.exclude))

        deps = [{'package_name': d.split('=')[0],
                 'package_version': d.split('=')[1],
                 'wheel_file': self.get_cached_wheel(package=d)} for d in self.config.get('dependencies')]

        wheel_files = [d for d in deps if d.get('wheel_file') is not None]
        for w in wheel_files:
            package_name = w.get('package_name')
            shutil.rmtree(str(temp_project_path / package_name), ignore_errors=True)
            with zipfile.ZipFile(w.get('wheel_file')) as zfile:
                # noinspection PyUnusedLocal
                files = [zfile.extract(f, temp_project_path) for f in zfile.namelist()
                         if f.startswith(f'{package_name}/')]
            # Anne tried to remove 'testing' as well -> numpy import errors
            shutil.rmtree(str(temp_project_path / package_name / 'tests'), ignore_errors=True)

        # Then zip it all up..
        print('Packaging project as zip...')

        compression_method = self.compression_method()

        self.zip_path.parent.mkdir(exist_ok=True, parents=True)
        with zipfile.ZipFile(self.zip_path, 'w', compression=compression_method) as zipf:

            for root, dirs, files in os.walk(str(temp_project_path)):

                for filename in files:
                    fp = Path(root, filename)
                    # Make sure that the files are all correctly chmodded
                    fp.chmod(0o755)

                    # Actually put the file into the proper place in the zip
                    print(fp.relative_to(temp_project_path))

                    zipi = zipfile.ZipInfo(str(fp.relative_to(temp_project_path)))
                    zipi.create_system = 3
                    zipi.external_attr = 0o755 << int(16)  # Is this P2/P3 functional?
                    with fp.open('rb') as f:
                        zipf.writestr(zipi, f.read(), compression_method)

                # Create python init file if it does not exist
                # Only do that if there are sub folders or python files and does not conflict with a neighbouring module
                # Related: https://github.com/Miserlou/Zappa/issues/766
                if not contains_python_files_or_subdirs(root):
                    # if the directory does not contain any .py file at any level, we can skip the rest
                    dirs[:] = [d for d in dirs if d != root]
                else:
                    if '__init__.py' not in files and not conflicts_with_a_neighbouring_module(root):
                        tmp_init = Path(temp_project_path, '__init__.py')
                        tmp_init.touch(0o755)

                        zipf.write(tmp_init,
                                   str(Path(root, '__init__.py').relative_to(temp_project_path)))

        # And, we're done!

        # Trash the temp directory
        shutil.rmtree(str(temp_project_path))

        return self

    def get_cached_wheel(self, package: str, disable_progress: bool = False):
        """
        Gets the locally stored version of a manylinux or pure python wheel. If one does not exist,
        the function downloads it.
        """
        cached_wheels_dir = Path(tempfile.gettempdir(), 'cached_wheels')
        cached_wheels_dir.mkdir(exist_ok=True, parents=True)

        try:
            wheel_url = self.wheels[package]
        except KeyError:
            logger.error(f'No wheel url found for {package}')
            return None

        wheel_file = wheel_url.split('/')[-1]
        wheel_path = Path(cached_wheels_dir, wheel_file)

        if not os.path.exists(wheel_path):
            # The file is not cached, download it.

            print(f' - {package}: Downloading')
            with open(wheel_path, 'wb') as f:
                self.download_url_with_progress(wheel_url, f, disable_progress)
        else:
            print(f' - {package}: Using locally cached linux wheel')

        return wheel_path

    @staticmethod
    def download_url_with_progress(url, stream, disable_progress):
        """
        Downloads a given url in chunks and writes to the provided stream (can be any io stream).
        Displays the progress bar for the download.
        """
        resp = requests.get(url, timeout=2, stream=True)
        resp.raw.decode_content = True

        progress = tqdm(unit='B', unit_scale=True, total=int(resp.headers.get('Content-Length', 0)),
                        disable=disable_progress)
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                progress.update(len(chunk))
                stream.write(chunk)

        progress.close()
