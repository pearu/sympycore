/*
  This extension module implements extension type Pair that holds two
  Python objects: head and data.

  The head part is assumed to be an immutable object. The data part
  can either be an immutable object or a Python dictionary, see below
  how the hash value is defined for Python dictionaries and what are
  other restrictions in such a case..

  There are three ways to access the parts of a Pair instance from
  Python:

    a = Pair(<head>, <data>)
    head, data = a.head, a.data     - for backward compatibility
    head, data = a.pair             - fastest way
 
  Note that head and data attributes are read-only. See
  sympycore/pair.py header for benchmark results.

  The hash value of a Pair instance is defined as follows:

    hash(a) := hash(tuple((a.head, a.data)))

  The data part can also be a Python dictionary, then the following
  definition for the hash value is used:

    hash(a) := hash(tuple((a.head, frozenset(a.data.items())))

  WARNING: Obviosly, when the hash value has been computed, then the
  program MUST NOT change the data dictionary (nor the dictionaries
  that are values). To check if it is safe to change the data
  dictionary, use is_writable attribute that returns True if hash has
  not been computed yet:

    a.is_writable -> True or False

  When adding new features to Pair type, make sure that these are
  added to pure Python class Pair in sympycore/pair.py as well.

  Author: Pearu Peterson
  Created: March 2008
 */

#include <Python.h>

typedef struct {
    PyObject_HEAD
    PyObject *pair;
    long hash;
} Pair;

static PyTypeObject PairType;

#define Pair_Check(op) PyObject_TypeCheck(op, &PairType)
#define Pair_CheckExact(op) ((op)->ob_type == &PairType)

static int
Pair_traverse(Pair *self, visitproc visit, void *arg)
{
  int vret;

  if (self->pair) {
    vret = visit(self->pair, arg);
    if (vret != 0)
      return vret;
  }
  return 0;
}

static int 
Pair_clear(Pair *self)
{
  PyObject *tmp = self->pair;
  self->pair = NULL;
  Py_XDECREF(tmp);
  return 0;
}

static void
Pair_dealloc(Pair* self)
{
  Pair_clear(self);
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Pair_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  Py_ssize_t len;
  Pair *self;

  self = (Pair *)type->tp_alloc(type, 0);

  if (self != NULL) {
    
    if (!PyTuple_Check(args)) {
      PyErr_SetString(PyExc_SystemError,
		      "new style getargs format but argument is not a tuple");
      return NULL;
    }

    len = PyTuple_GET_SIZE(args);
    if (len!=2) {
      PyErr_SetString(PyExc_TypeError,
		      "Pair.__new__ expects exactly 2 arguments: (head, data)");
      return NULL;
    }

    self->pair = args;    
    self->hash = -1;
    Py_INCREF(self->pair);

  }

    return (PyObject *)self;
}

static long dict_hash(PyObject *d);

static long
tuple2_hash(PyObject *item0, PyObject *item1) {
  register long hash, h;
  long mult = 1000003L;
  hash = 0x345678L;
  h = PyObject_Hash(item0);
  if (h==-1)
    return h;
  hash = (hash ^ h) * mult;
  mult += 82522L;
  if (PyDict_Check(item1)) {
    h = dict_hash(item1);
  } else
    h = PyObject_Hash(item1);
  if (h==-1)
    return h;
  hash = (hash ^ h) * mult;
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
    if (h==-1)
      return h;
    hash ^= (h ^ (h << 16) ^ 89869747L)  * 3644798167u;
  }
  hash = hash * 69069L + 907133923L;
  if (hash == -1)
    hash = 590923713L;
  return hash;
}

/*
  if isinstance(y, dict):
    hash(Pair(x,y)) == hash((x,frozenset(y.items()))
  else:
    hash(Pair(x,y)) == hash((x,y))
 */
static long
Pair_hash(PyObject *self)
{
  Pair *o = (Pair *)self;
  if (o->hash!=-1)
    return o->hash;
  o->hash = tuple2_hash(PyTuple_GET_ITEM(o->pair, 0), PyTuple_GET_ITEM(o->pair, 1));
  return o->hash;
}

static PyObject *
Pair_gethead(Pair *self, void *closure)
{
  PyObject *obj = PyTuple_GET_ITEM(self->pair, 0);
  Py_INCREF(obj);
  return obj;
  //  return self->head;
}

static PyObject *
Pair_getdata(Pair *self, void *closure)
{
  PyObject *obj = PyTuple_GET_ITEM(self->pair, 1);
  Py_INCREF(obj);
  return obj;
}

static PyObject *
Pair_getis_writable(Pair *self, void *closure)
{
  if (self->hash==-1) {
    Py_RETURN_TRUE;
  }
  Py_RETURN_FALSE;
}

static PyObject *
Pair_getpair(Pair *self, void *closure)
{
  Py_INCREF(self->pair);
  return self->pair;
}

static PyObject *
Pair_repr(Pair *v)
{
  return PyString_Format(PyString_FromString("%s%r"),
			 PyTuple_Pack(2,
				      PyString_FromString(v->ob_type->tp_name), 
				      v->pair));
}

static PyGetSetDef Pair_getseters[] = {
    {"head", (getter)Pair_gethead, NULL,
     "read-only head attribute", NULL},
    {"data", (getter)Pair_getdata, NULL, 
     "read-only data attribute", NULL},
    {"pair", (getter)Pair_getpair, NULL, 
     "read-only (head, data) attribute", NULL},
    {"is_writable", (getter)Pair_getis_writable, NULL, 
     "True when hash has not been computed", NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject PairType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "pair_ext.Pair",           /*tp_name*/
  sizeof(Pair),              /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor)Pair_dealloc,  /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  (reprfunc)Pair_repr,       /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  Pair_hash,                 /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
  "Holds a pair (head, data).", /* tp_doc */
  (traverseproc)Pair_traverse,  /* tp_traverse */
  (inquiry)Pair_clear,       /* tp_clear */
  0,	                     /* tp_richcompare */
  0,	                     /* tp_weaklistoffset */
  0,	                     /* tp_iter */
  0,	                     /* tp_iternext */
  0,                         /* tp_methods */
  0,                         /* tp_members */
  Pair_getseters,            /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  0,                         /* tp_init */
  0,                         /* tp_alloc */
  Pair_new,                  /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initpair_ext(void) 
{
  PyObject* m;
  
  if (PyType_Ready(&PairType) < 0)
    return;
  
  m = Py_InitModule3("pair_ext", module_methods,
		     "Provides extension type Pair.");
  
  if (m == NULL)
    return;
  
  Py_INCREF(&PairType);
  PyModule_AddObject(m, "Pair", (PyObject *)&PairType);
}
