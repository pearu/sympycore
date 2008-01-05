#ifdef __cplusplus
extern "C" {
#endif
#define NO_USE_JUST_CHEAT_EMACS }

#include "Python.h"

static PyObject* zero;
static PyObject* one;

static
int c_add_inplace_dict_term_coeff(PyObject *d, PyObject *t, PyObject *c) {
  /* return 0 on success */
  PyObject* b = PyDict_GetItem(d, t);
  PyObject* c1 = NULL;
  if (b==NULL) {
    Py_INCREF(c);
    return PyDict_SetItem(d, t, c);
  }
  if ((c1 = PyNumber_Add(b, c))==NULL) return 1;
  if (c1==zero) {
    return PyDict_DelItem(d, t);
  }
  Py_INCREF(c1);
  return PyDict_SetItem(d, t, c1);
}

static
int c_add_inplace_dict_terms(PyObject *d, PyObject *rhs, PyObject *c) {
  /* return 0 on success */
  PyObject* it = PyObject_GetIter(PyTuple_GET_ITEM(rhs,1));
  PyObject* item = NULL;
  PyObject* t = NULL;
  PyObject* c1 = NULL;
  if (it==NULL) return 1;
  while ((item = PyIter_Next(it))!=NULL) {
    /*
    if ((!PyTuple_CheckExact(item)) || (PyTuple_GET_SIZE(item)!=2)) {
      PyErr_SetString(PyExc_TypeError,"expected 2-tuple item");
      Py_DECREF(item);
      Py_DECREF(it);
      return 1;
    }
    */
    t = PyTuple_GET_ITEM(item, 0);
    if (c==one) {
      c1 = c;
    } else if ((c1 = PyNumber_Multiply(PyTuple_GET_ITEM(item, 1), c))==NULL) {
      Py_DECREF(item);
      Py_DECREF(it);
      return 1;
    }
    c_add_inplace_dict_term_coeff(d, t, c1);
    Py_DECREF(item);
  }
  Py_DECREF(it);
  if (PyErr_Occurred()) return 1;
  return 0;
}

static
int c_add_inplace_dict_terms1(PyObject *d, PyObject *rhs) {
  /* return 0 on success */
  PyObject* it = PyObject_GetIter(PyTuple_GET_ITEM(rhs,1));
  PyObject* item = NULL;
  PyObject* t = NULL;
  PyObject* c = NULL;
  if (it==NULL) return 1;
  while ((item = PyIter_Next(it))!=NULL) {
    /*
    if ((!PyTuple_CheckExact(item)) || (PyTuple_GET_SIZE(item)!=2)) {
      PyErr_SetString(PyExc_TypeError,"expected 2-tuple item");
      Py_DECREF(item);
      Py_DECREF(it);
      return 1;
    }
    */
    t = PyTuple_GET_ITEM(item, 0);
    c = PyTuple_GET_ITEM(item, 1);
    c_add_inplace_dict_term_coeff(d, t, c);
    Py_DECREF(item);
  }
  Py_DECREF(it);
  if (PyErr_Occurred()) return 1;
  return 0;
}

static PyObject* add_inplace_dict_term_coeff(PyObject *self, PyObject *args) {
  PyObject* d=NULL;
  PyObject* t=NULL;
  PyObject* c=NULL;
  if (!PyArg_ParseTuple(args, "O!O!O", &PyDict_Type, &d, &PyTuple_Type, &t, &c))
    return NULL;
  if (c_add_inplace_dict_term_coeff(d, t, c)) return NULL;
  return Py_BuildValue("");
}

static PyObject* add_inplace_dict_terms(PyObject *self, PyObject *args) {
  PyObject* d=NULL;
  PyObject* rhs=NULL;
  PyObject* c=NULL;
  if (!PyArg_ParseTuple(args, "O!O!O", &PyDict_Type, &d, &PyTuple_Type, &rhs, &c))
    return NULL;
  if (PyTuple_GET_SIZE(rhs)<2) {
    PyErr_SetString(PyExc_TypeError,"expected 2 or 3-tuple rhs");
    return NULL;
  }
  if (c==one) {
    if (c_add_inplace_dict_terms1(d, rhs)) return NULL;
  } else {
    if (c_add_inplace_dict_terms(d, rhs, c)) return NULL;
  }
  return Py_BuildValue("");
}

static PyObject* add_inplace_dict_terms1(PyObject *self, PyObject *args) {
  PyObject* d=NULL;
  PyObject* rhs=NULL;
  if (!PyArg_ParseTuple(args, "O!O!", &PyDict_Type, &d, &PyTuple_Type, &rhs))
    return NULL;
  if (PyTuple_GET_SIZE(rhs)<2) {
    PyErr_SetString(PyExc_TypeError,"expected 2 or 3-tuple rhs");
    return NULL;
  }
  if (c_add_inplace_dict_terms1(d, rhs)) return NULL;
  return Py_BuildValue("");
}

static PyObject* init_singletons(PyObject *self, PyObject *args) {
  if (!PyArg_ParseTuple(args, "OO", &zero, &one)) return NULL;
  return Py_BuildValue("");
}

static
PyMethodDef module_methods[] = {
  {"add_inplace_dict_term_coeff", add_inplace_dict_term_coeff, METH_VARARGS, "add_inplace_dict_term_coeff doc"},
  {"add_inplace_dict_terms", add_inplace_dict_terms, METH_VARARGS, "add_inplace_dict_terms doc"},
  {"add_inplace_dict_terms1", add_inplace_dict_terms1, METH_VARARGS, "add_inplace_dict_terms1 doc"},
  {"init", init_singletons, METH_VARARGS, "init(zero, one)"},
  {NULL,NULL,0,NULL}
};
static
char module_doc[] = "";


PyMODINIT_FUNC
initc_sexpr(void) {
  if (Py_InitModule3("c_sexpr", module_methods, module_doc)==NULL) goto capi_error;
  return;
 capi_error:
  if (!PyErr_Occurred()) {
    PyErr_SetString(PyExc_RuntimeError, "failed to initialize c_sexpr module.");
  }
  return;
}

#ifdef __cplusplus
}
#endif
