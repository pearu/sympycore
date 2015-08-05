from numpy.testing import *

set_package_path()
from symbolic.api import Symbolic, Boolean, And, Or, Not, TRUE, FALSE
restore_path()
Symbolic.interactive = False

class test_Boolean(NumpyTestCase):

    def check_init(self):
        assert_equal(Symbolic(True).tostr(),'TRUE')
        assert_equal(Symbolic(False).tostr(),'FALSE')
        assert_equal(Symbolic('True').tostr(),'TRUE')
        assert_equal(Symbolic('false').tostr(),'FALSE')
        assert_equal(TRUE.tostr(),'TRUE')
        assert_equal(FALSE.tostr(),'FALSE')

    def check_invert(self):
        assert_equal((~TRUE).tostr(),'FALSE')
        assert_equal((~FALSE).tostr(),'TRUE')
        assert_equal(Symbolic('~ FALSE').tostr(),'TRUE')
        assert_equal(Symbolic('not FALSE').tostr(),'TRUE')

    def check_and(self):
        assert_equal((TRUE & TRUE).tostr(),'TRUE')
        assert_equal((TRUE & FALSE).tostr(),'FALSE')
        assert_equal(Symbolic('TRUE & TRUE').tostr(),'TRUE')
        assert_equal(Symbolic('TRUE and TRUE').tostr(),'TRUE')
        assert_equal(Symbolic('TRUE & FALSE').tostr(),'FALSE')
        assert_equal(Symbolic('TRUE & ~FALSE').tostr(),'TRUE')

    def check_or(self):
        assert_equal((FALSE | TRUE).tostr(),'TRUE')
        assert_equal((FALSE | FALSE).tostr(),'FALSE')
        assert_equal(Symbolic('TRUE | TRUE').tostr(),'TRUE')
        assert_equal(Symbolic('TRUE or TRUE').tostr(),'TRUE')
        assert_equal(Symbolic('TRUE | FALSE').tostr(),'TRUE')
        assert_equal(Symbolic('FALSE | FALSE').tostr(),'FALSE')
        assert_equal(Symbolic('~FALSE | FALSE').tostr(),'TRUE')

    def check_xor(self):
        assert_equal((TRUE ^ TRUE).tostr(),'FALSE')
        assert_equal((TRUE ^ FALSE).tostr(),'TRUE')
        assert_equal((FALSE ^ TRUE).tostr(),'TRUE')
        assert_equal((FALSE ^ FALSE).tostr(),'FALSE')
        assert_equal(Symbolic('TRUE ^ TRUE').tostr(),'FALSE')
        assert_equal(Symbolic('TRUE xor TRUE').tostr(),'FALSE')
        assert_equal(Symbolic('TRUE ^ FALSE').tostr(),'TRUE')
        assert_equal(Symbolic('TRUE ^ ~TRUE').tostr(),'TRUE')

    def _check_pos(self):
        assert_equal((+TRUE).tostr(),'TRUE2')

    def check_bool(self):
        assert_equal(bool(TRUE), True)
        assert_equal(bool(FALSE), False)

if __name__ == '__main__':
    NumpyTest().run()
