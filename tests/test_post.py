import os
import shutil
import sys

import pytest

from conda_build import post, api
from conda_build.utils import on_win, package_has_file

from .utils import add_mangling, metadata_dir


def test_compile_missing_pyc(testing_workdir):
    good_files = ['f1.py', 'f3.py']
    bad_file = 'f2_bad.py'
    tmp = os.path.join(testing_workdir, 'tmp')
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'test-recipes',
                                 'metadata', '_compile-test'), tmp)
    post.compile_missing_pyc(os.listdir(tmp), cwd=tmp,
                                python_exe=sys.executable)
    for f in good_files:
        assert os.path.isfile(os.path.join(tmp, add_mangling(f)))
    assert not os.path.isfile(os.path.join(tmp, add_mangling(bad_file)))


@pytest.mark.skipif(on_win, reason="no linking on win")
def test_hardlinks_to_copies(testing_workdir):
    with open('test1', 'w') as f:
        f.write("\n")

    os.link('test1', 'test2')
    assert os.lstat('test1').st_nlink == 2
    assert os.lstat('test2').st_nlink == 2

    post.make_hardlink_copy('test1', os.getcwd())
    post.make_hardlink_copy('test2', os.getcwd())

    assert os.lstat('test1').st_nlink == 1
    assert os.lstat('test2').st_nlink == 1


def test_postbuild_files_raise(testing_metadata, testing_workdir):
    fn = 'buildstr', 'buildnum', 'version'
    for f in fn:
        with open(os.path.join(testing_metadata.config.work_dir,
                               '__conda_{}__.txt'.format(f)), 'w') as fh:
            fh.write('123')
        with pytest.raises(ValueError) as exc:
            post.get_build_metadata(testing_metadata)
        assert f in str(exc)


def test_postlink_script_in_output_explicit(testing_config):
    recipe = os.path.join(metadata_dir, '_post_link_in_output')
    pkg = api.build(recipe, config=testing_config, notest=True)[0]
    assert (package_has_file(pkg, 'bin/.out1-post-link.sh') or
            package_has_file(pkg, 'Scripts/.out1-post-link.bat'))


def test_postlink_script_in_output_implicit(testing_config):
    recipe = os.path.join(metadata_dir, '_post_link_in_output_implicit')
    pkg = api.build(recipe, config=testing_config, notest=True)[0]
    assert (package_has_file(pkg, 'bin/.out1-post-link.sh') or
            package_has_file(pkg, 'Scripts/.out1-post-link.bat'))
