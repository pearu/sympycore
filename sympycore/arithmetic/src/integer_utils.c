#ifdef __cplusplus
extern "C" {
#endif
#define NO_USE_JUST_CHEAT_EMACS }

#include "Python.h"

static PyObject* gcd(PyObject *self, PyObject *args) {
  long a, b;
  if (!PyArg_ParseTuple(args, "ll", &a, &b)) return NULL;
  while (a) {
    a = b % a;
    b = a;
  }
  return Py_BuildValue("l", b);
}

static
PyMethodDef module_methods[] = {
  {"c_gcd", gcd, METH_VARARGS, "gcd doc"},
  {NULL,NULL,0,NULL}
};
static
char module_doc[] = "";


PyMODINIT_FUNC
initinteger_utils(void) {
  if (Py_InitModule3("integer_utils", module_methods, module_doc)==NULL) goto capi_error;
  return;
 capi_error:
  if (!PyErr_Occurred()) {
    PyErr_SetString(PyExc_RuntimeError, "failed to initialize integer_utils module.");
  }
  return;
}

#ifdef __cplusplus
}
#endif
