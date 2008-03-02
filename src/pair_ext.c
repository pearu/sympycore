#include <Python.h>
//#include "structmember.h"

typedef struct {
    PyObject_HEAD
    PyObject *head;
    PyObject *data;
    long hash;
} Pair;

static PyTypeObject PairType;

#define Pair_Check(op) PyObject_TypeCheck(op, &PairType)
#define Pair_CheckExact(op) ((op)->ob_type == &PairType)

static int
Pair_traverse(Pair *self, visitproc visit, void *arg)
{
  int vret;

  if (self->head) {
    vret = visit(self->head, arg);
    if (vret != 0)
      return vret;
  }
  if (self->data) {
    vret = visit(self->data, arg);
    if (vret != 0)
      return vret;
  }
  
  return 0;
}

static int 
Pair_clear(Pair *self)
{
  PyObject *tmp;
  
  tmp = self->head;
  self->head = NULL;
  Py_XDECREF(tmp);
  
  tmp = self->data;
  self->data = NULL;
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

    self->head = PyTuple_GET_ITEM(args, 0);
    if (self->head==NULL) {
      Py_DECREF(self);
      return NULL;
    }

    self->data = PyTuple_GET_ITEM(args, 1);
    if (self->data==NULL) {
      Py_DECREF(self);
      return NULL;
    }

    Py_INCREF(self->head);
    Py_INCREF(self->data);
    
    self->hash = -1;
  }

    return (PyObject *)self;
}

static PyObject *
Pair_item(register Pair *self, register Py_ssize_t i)
{
  if (i==0) {
    Py_INCREF(self->head);
    return self->head;
  }
  if (i==1) {
    Py_INCREF(self->data);
    return self->data;
  }
  PyErr_SetString(PyExc_IndexError, "Pair index out of range [0,1]");
  return NULL;
}

PyObject *
Pair_slice(PyObject *op, Py_ssize_t i, Py_ssize_t j)
{
  Py_ssize_t len;
  register PyTupleObject *np;
  register Pair *self = (Pair*)op;
  if (op == NULL || !Pair_Check(op)) {
    PyErr_BadInternalCall();
    return NULL;
  }
  if (i<0) i=0;
  if (j>2) j=2;
  if (j<i) j=i;
  len = j-i;
  np = (PyTupleObject *)PyTuple_New(len);
  if (len==2) {
    PyObject *v = self->head;
    Py_INCREF(v);
    np->ob_item[0] = v;
    v = self->data;
    Py_INCREF(v);
    np->ob_item[1] = v;
  } else if ((len==1) && (i==0)) {
    PyObject *v = self->head;
    Py_INCREF(v);
    np->ob_item[0] = v;
  } else if ((len==1) && (i==1)) {
    PyObject *v = self->data;
    Py_INCREF(v);
    np->ob_item[0] = v;
  }
  return (PyObject *)np;
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
  o->hash = tuple2_hash(o->head, o->data);
  return o->hash;
}

static PyObject *
Pair_gethead(Pair *self, void *closure)
{
    Py_INCREF(self->head);
    return self->head;
}

static PyObject *
Pair_getdata(Pair *self, void *closure)
{
    Py_INCREF(self->data);
    return self->data;
}

static PyObject *
Pair_repr(Pair *v)
{
  return PyString_Format(PyString_FromString("%s(%r, %r)"),
			 PyTuple_Pack(3,
				      PyString_FromString(v->ob_type->tp_name), 
				      v->head,
				      v->data));
}

static PyGetSetDef Pair_getseters[] = {
    {"head", (getter)Pair_gethead, NULL, "head", NULL},
    {"data", (getter)Pair_getdata, NULL, "data", NULL},
    {NULL}  /* Sentinel */
};

/*
  Pair_item provides a fast way to access head and data data member.
  Pair_slice is used in a idiom `head, data = <Pair instance>[:]`.
 */

static PySequenceMethods Pair_as_sequence = {
  0,                                      /* sq_length */
  0,                                      /* sq_concat */
  0,                                      /* sq_repeat */
  (ssizeargfunc)Pair_item,                /* sq_item */
  (ssizessizeargfunc)Pair_slice,          /* sq_slice */
  0,                                      /* sq_ass_item */
  0,                                      /* sq_ass_slice */
  0,              /* sq_contains */
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
  &Pair_as_sequence,         /*tp_as_sequence*/
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
