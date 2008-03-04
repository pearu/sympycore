/*
  This extension module implements extension type Expr that holds two
  Python objects, head and data, in a pair attribute.

  When adding new features to Expr type, make sure that these are
  added also to pure Python class Expr in sympycore/expr.py.

  Author: Pearu Peterson
  Created: March 2008
 */

static char Expr_doc[] = \
  "Represents an symbolic expression in a pair form: (head, data)\n"	\
  "\n"									\
  "The pair (head, data) is saved in an attribute ``pair``. The parts of\n" \
  "a pair, head and data, can be also accessed via ``head`` and ``data``\n" \
  "attributes, respectively. All three attributes are read-only.\n"	\
  "\n"									\
  "The head part is assumed to be an immutable object.\n"		\
  "The data part can be either an immutable object or Python dictionary.\n" \
  "In the former case, the hash value of Expr instance is defined as::\n" \
  "\n"									\
  "  hash((<Expr>.head, <Expr>.data))\n"				\
  "\n"									\
  "Otherwise, if ``data`` contains a Python dictionary, then the hash\n" \
  "value is defined as::\n"						\
  "\n"									\
  "  hash((<Expr>.head, frozenset(<Expr>.data.items())))\n"		\
  "\n"									\
  "WARNING: the hash value of an Expr instance is computed (and cached)\n"\
  "when it is used as a key to Python dictionary. This means that the\n"\
  "instance content MUST NOT be changed after the hash is computed.  To\n" \
  "check if it is safe to change the ``data`` dictionary, use\n"	\
  "``is_writable`` attribute that returns True when the hash value has\n" \
  "not been computed::\n"						\
  "\n"									\
  "  <Expr>.is_writable -> True or False\n"				\
  "\n"									\
  "There are two ways to access the parts of a Expr instance from\n"	\
  "Python::\n"								\
  "\n"									\
  "    a = Expr(<head>, <data>)\n"					\
  "    head, data = a.head, a.data     - for backward compatibility\n"	\
  "    head, data = a.pair             - fastest way\n"			\
  "\n"									\
  "This is C version of Expr type.\n"
;

#include <Python.h>

typedef struct {
  PyObject_HEAD
  PyObject *pair;
  long hash;
} Expr;

static PyTypeObject ExprType;

#define Expr_Check(op) PyObject_TypeCheck(op, &ExprType)
#define Expr_CheckExact(op) ((op)->ob_type == &ExprType)

static int
Expr_traverse(Expr *self, visitproc visit, void *arg)
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
Expr_clear(Expr *self)
{
  PyObject *tmp = self->pair;
  self->pair = NULL;
  Py_XDECREF(tmp);
  return 0;
}

static void
Expr_dealloc(Expr* self)
{
  Expr_clear(self);
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Expr_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  Py_ssize_t len;
  Expr *self = (Expr *)type->tp_alloc(type, 0);

  if (self != NULL) {
    
    if (!PyTuple_Check(args)) {
      PyErr_SetString(PyExc_SystemError,
		      "new style getargs format but argument is not a tuple");
      return NULL;
    }

    len = PyTuple_GET_SIZE(args);
    if (len!=2) {
      PyErr_SetString(PyExc_TypeError,
		      "Expr.__new__ expects exactly 2 arguments: (head, data)");
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
    hash(Expr(x,y)) == hash((x,frozenset(y.items()))
  else:
    hash(Expr(x,y)) == hash((x,y))
 */
static long
Expr_hash(PyObject *self)
{
  Expr *o = (Expr *)self;
  if (o->hash!=-1)
    return o->hash;
  o->hash = tuple2_hash(PyTuple_GET_ITEM(o->pair, 0), PyTuple_GET_ITEM(o->pair, 1));
  return o->hash;
}

static PyObject *
Expr_gethead(Expr *self, void *closure)
{
  PyObject *obj = PyTuple_GET_ITEM(self->pair, 0);
  Py_INCREF(obj);
  return obj;
}

static PyObject *
Expr_getdata(Expr *self, void *closure)
{
  PyObject *obj = PyTuple_GET_ITEM(self->pair, 1);
  Py_INCREF(obj);
  return obj;
}

static PyObject *
Expr_getis_writable(Expr *self, void *closure)
{
  if (self->hash==-1) {
    Py_RETURN_TRUE;
  }
  Py_RETURN_FALSE;
}

static PyObject *
Expr_getpair(Expr *self, void *closure)
{
  Py_INCREF(self->pair);
  return self->pair;
}

static PyObject *
Expr_repr(Expr *self)
{
  return PyString_Format(PyString_FromString("%s%r"),
			 PyTuple_Pack(2,
				      PyString_FromString(self->ob_type->tp_name), 
				      self->pair));
}

static PyGetSetDef Expr_getseters[] = {
    {"head", (getter)Expr_gethead, NULL,
     "read-only head attribute", NULL},
    {"data", (getter)Expr_getdata, NULL, 
     "read-only data attribute", NULL},
    {"pair", (getter)Expr_getpair, NULL, 
     "read-only (head, data) attribute", NULL},
    {"is_writable", (getter)Expr_getis_writable, NULL, 
     "True when hash has not been computed", NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject ExprType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "Expr",           /*tp_name*/
  sizeof(Expr),              /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor)Expr_dealloc,  /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  (reprfunc)Expr_repr,       /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  Expr_hash,                 /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
  Expr_doc,                  /* tp_doc */
  (traverseproc)Expr_traverse,  /* tp_traverse */
  (inquiry)Expr_clear,       /* tp_clear */
  0,	                     /* tp_richcompare */
  0,	                     /* tp_weaklistoffset */
  0,	                     /* tp_iter */
  0,	                     /* tp_iternext */
  0,                         /* tp_methods */
  0,                         /* tp_members */
  Expr_getseters,            /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  0,                         /* tp_init */
  0,                         /* tp_alloc */
  Expr_new,                  /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initexpr_ext(void) 
{
  PyObject* m;
  
  if (PyType_Ready(&ExprType) < 0)
    return;
  
  m = Py_InitModule3("expr_ext", module_methods,
		     "Provides extension type Expr.");
  
  if (m == NULL)
    return;
  
  Py_INCREF(&ExprType);
  PyModule_AddObject(m, "Expr", (PyObject *)&ExprType);
}
