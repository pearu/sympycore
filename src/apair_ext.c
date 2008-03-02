#include <Python.h>
#include "structmember.h"

typedef struct {
    PyObject_HEAD
    PyObject *first;
    PyObject *last;
    long hash;
} APair;

static int
APair_traverse(APair *self, visitproc visit, void *arg)
{
  int vret;

  if (self->first) {
    vret = visit(self->first, arg);
    if (vret != 0)
      return vret;
  }
  if (self->last) {
    vret = visit(self->last, arg);
    if (vret != 0)
      return vret;
  }
  
  return 0;
}

static int 
APair_clear(APair *self)
{
  PyObject *tmp;
  
  tmp = self->first;
  self->first = NULL;
  Py_XDECREF(tmp);
  
  tmp = self->last;
  self->last = NULL;
  Py_XDECREF(tmp);
  
  return 0;
}

static void
APair_dealloc(APair* self)
{
  APair_clear(self);
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
APair_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  Py_ssize_t len;
  APair *self;

  self = (APair *)type->tp_alloc(type, 0);

  if (self != NULL) {
    
    if (!PyTuple_Check(args)) {
      PyErr_SetString(PyExc_SystemError,
		      "new style getargs format but argument is not a tuple");
      return NULL;
    }
    len = PyTuple_GET_SIZE(args);
    if (len!=2) {
      PyErr_SetString(PyExc_TypeError,
		      "APair.__new__ expects exactly 2 arguments: (first, last)");
      return NULL;
    }

    self->first = PyTuple_GET_ITEM(args, 0);
    if (self->first==NULL) {
      Py_DECREF(self);
      return NULL;
    }
    self->last = PyTuple_GET_ITEM(args, 1);
    if (self->last==NULL) {
      Py_DECREF(self);
      return NULL;
    }
    Py_INCREF(self->first);
    Py_INCREF(self->last);
    
    self->hash = -1;
  }

    return (PyObject *)self;
}

static PyObject *
APairitem(register APair *self, register Py_ssize_t i)
{
  if (i==0) {
    Py_INCREF(self->first);
    return self->first;
  }
  if (i==1) {
    Py_INCREF(self->last);
    return self->last;
  }
  PyErr_SetString(PyExc_IndexError, "APair index out of range [0,1]");
  return NULL;
}

static long dict_hash(PyObject *d);

static long
tuple2_hash(PyObject *item0, PyObject *item1) {
  register long hash, h;
  long mult = 1000003L;
  hash = 0x345678L;
  h = PyObject_Hash(item0);
  hash = (hash ^ h) * mult;
  mult += 82524L;
  if (PyDict_Check(item1)) {
    h = dict_hash(item1);
  } else
    h = PyObject_Hash(item1);
  hash = (hash ^ h) * mult;
  mult += 82524L;
  hash += 97531L;
  if (hash==-1)
    hash = -2;
  return hash;
}

/*
  hash(dict) == hash(frozenset(dict.items()))
 */
static long
dict_hash(PyObject *d) {
  Py_ssize_t i;
  PyObject *key, *value;
  long h, hash = 1927868237L;
  hash *= PyDict_Size(d) + 1;
  i = 0;
  while (PyDict_Next(d, &i, &key, &value)) {
    h = tuple2_hash(key, value);
    hash ^= (h ^ (h << 16) ^ 89869747L)  * 3644798167u;
  }
  hash = hash * 69069L + 907133923L;
  if (hash == -1)
    hash = 590923713L;
  return hash;
}

/*
  if isinstance(y, dict):
    hash(APair(x,y)) == hash((x,frozenset(y.items()))
  else:
    hash(APair(x,y)) == hash((x,y))
 */
static long
APair_hash(PyObject *self)
{
  APair *o = (APair *)self;
  if (o->hash!=-1)
    return o->hash;
  o->hash = tuple2_hash(o->first, o->last);
  return o->hash;
}

static PyMemberDef APair_members[] = {
    {"head", T_OBJECT_EX, offsetof(APair, first), 0,
     "first name"},
    {"data", T_OBJECT_EX, offsetof(APair, last), 0,
     "last name"},
    {"last_hash", T_LONG, offsetof(APair, hash), 0,
     "last hash value or -1"},
    {NULL}  /* Sentinel */
};

static PyObject *
APair_name(APair* self)
{
    static PyObject *format = NULL;
    PyObject *args, *result;

    if (format == NULL) {
        format = PyString_FromString("%s %s");
        if (format == NULL)
            return NULL;
    }

    if (self->first == NULL) {
        PyErr_SetString(PyExc_AttributeError, "first");
        return NULL;
    }

    if (self->last == NULL) {
        PyErr_SetString(PyExc_AttributeError, "last");
        return NULL;
    }

    args = Py_BuildValue("OO", self->first, self->last);
    if (args == NULL)
        return NULL;

    result = PyString_Format(format, args);
    Py_DECREF(args);
    
    return result;
}

static PyMethodDef APair_methods[] = {
  {"name", (PyCFunction)APair_name, METH_NOARGS,
   "Return the name, combining the first and last name"
  },
    {NULL}  /* Sentinel */
};

/*
  APairitem provides a fast way to access first and last data member.
 */

static PySequenceMethods APair_as_sequence = {
  0,                                      /* sq_length */
  0,                                      /* sq_concat */
  0,                                      /* sq_repeat */
  (ssizeargfunc)APairitem,                /* sq_item */
  0,                                      /* sq_slice */
  0,                                      /* sq_ass_item */
  0,                                      /* sq_ass_slice */
  0,              /* sq_contains */
};

static PyTypeObject APairType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "apair_ext.APair",         /*tp_name*/
  sizeof(APair),             /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor)APair_dealloc, /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  &APair_as_sequence,        /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  &APair_hash,                /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
  "Contains a pair (first, last)", /* tp_doc */
  (traverseproc)APair_traverse,    /* tp_traverse */
  (inquiry)APair_clear,      /* tp_clear */
  0,		               /* tp_richcompare */
  0,		               /* tp_weaklistoffset */
  0,		               /* tp_iter */
  0,		               /* tp_iternext */
  APair_methods,             /* tp_methods */
  APair_members,             /* tp_members */
  0,                         /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  0,                         /* tp_init */
  0,                         /* tp_alloc */
  APair_new,                 /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initapair_ext(void) 
{
  PyObject* m;
  
  if (PyType_Ready(&APairType) < 0)
    return;
  
  m = Py_InitModule3("apair_ext", module_methods,
		     "Provides extension type APair.");
  
  if (m == NULL)
    return;
  
  Py_INCREF(&APairType);
  PyModule_AddObject(m, "APair", (PyObject *)&APairType);
}
