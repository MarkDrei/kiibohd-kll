'''
Test functions/libraries for the kll compiler
'''

### Imports ###

import kll
import os
import pytest
import tempfile
from git import Repo, exc



### Variables ###

# Tests run against this fork's firmware rather than upstream, so that a change
# here is validated against the controller it is actually used with. Either may
# be pointed at a local checkout, which also keeps the tests offline.
CONTROLLER_REPO = os.environ.get('KLL_TEST_CONTROLLER_REPO', 'https://github.com/MarkDrei/kiibohd-Controller.git')
KLL_REPO = os.environ.get('KLL_TEST_KLL_REPO', 'https://github.com/MarkDrei/kiibohd-kll.git')


### Functions ###

def header_test(name, args):
    '''
    Prints out the name of the test and the arguments passed

    @param name: Name of the test
    @param args: List of arguments
    '''
    print('\n---- {} ---- {}'.format(name, args))

def kll_run(args):
    '''
    Run kll compiler

    @return: Exit code
    '''
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        kll.main(args)
    assert pytest_wrapped_e.type == SystemExit
    return pytest_wrapped_e.value.code

def _ensure_git_checkout(source, cache_dir):
    '''
    Return a usable git checkout of source.

    Existing local directories are used in place so tests can run offline and
    CI can point at a previously checked-out tree. Remote URLs are cloned into
    cache_dir (or updated if a clone is already present).
    '''
    if os.path.isdir(source):
        return os.path.abspath(source)

    try:
        if not os.path.isdir(cache_dir):
            Repo.clone_from(source, cache_dir)
        else:
            repo = Repo(cache_dir)
            repo.remotes.origin.fetch('+refs/heads/*:refs/remotes/origin/*')
            repo.remotes.origin.pull()
    except exc.GitCommandError:
        # Concurrent test processes may be initializing the same cache
        pass

    return cache_dir


@pytest.fixture(scope="session")
def kiibohd_controller_repo():
    '''
    Downloads a cached copy of the kiibohd controller repo
    '''
    tmp_dir = os.path.join(tempfile.gettempdir(), 'kll_controller_test')
    controller_dir = _ensure_git_checkout(CONTROLLER_REPO, tmp_dir)

    # Nested kll clone is only for remote/cache checkouts. Never write into a
    # caller-supplied local controller tree.
    if not os.path.isdir(CONTROLLER_REPO):
        kll_dir = os.path.join(controller_dir, 'kll')
        _ensure_git_checkout(KLL_REPO, kll_dir)

    return controller_dir

