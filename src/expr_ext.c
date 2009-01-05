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
  "If ``data`` is a Python list, then the hash value is::"		\
  "\n"									\
  "  hash((<Expr>.head, tuple(<Expr>.data)))\n"				\
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
  "When Expr constructor is called with one argument, say ``x``, then\n"\
  "``<Expr subclass>.convert(x)`` will be returned\n"                   \
  "\nThis is C version of Expr type.\n"
;

#include <Python.h>

typedef struct {
  PyObject_HEAD
  PyObject *pair;
  long hash;
} Expr;

static PyTypeObject ExprType;
static PyTypeObject PairType;

static PyObject* NUMBER;
static PyObject* SYMBOL;
static PyObject* SPECIAL;
static PyObject* Expr_as_lowlevel(Expr *self);
static PyObject* str_as_lowlevel;
static PyObject* str_convert;
static PyObject* str_handle_numeric_item;
static PyObject* str_getinitargs;

#define Expr_Check(op) PyObject_TypeCheck(op, &ExprType)
#define Expr_CheckExact(op) ((op)->ob_type == &ExprType)
#define Pair_Check(op) PyObject_TypeCheck(op, &PairType)
#define Pair_CheckExact(op) ((op)->ob_type == &PairType)

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
Expr_new(PyTypeObject *type, PyObject *args, PyObject *kws)
{
  Py_ssize_t len;
  Expr *self = NULL;
 
  if (!PyTuple_Check(args)) {
    PyErr_SetString(PyExc_SystemError,
		    "new style getargs format but argument is not a tuple");
    return NULL;
  }

  len = PyTuple_GET_SIZE(args);
  if (len==1)
    return PyObject_CallMethodObjArgs((PyObject*)type,
				      str_convert,
				      PyTuple_GET_ITEM(args, 0),
				      NULL
				      );  
  if (len!=2) {
    PyErr_SetString(PyExc_TypeError,
		    "Expr.__new__ expects 1 or 2 arguments: obj or (head, data)");
    return NULL;
  }
  
  self = (Expr *)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->pair = args;    
    self->hash = -1;
    Py_INCREF(self->pair);
  }
  return (PyObject *)self;
}

static PyObject *
Pair_new(PyTypeObject *type, PyObject *args, PyObject *kws)
{
  Py_ssize_t len;
  Expr *self = NULL;
 
  if (!PyTuple_Check(args)) {
    PyErr_SetString(PyExc_SystemError,
		    "new style getargs format but argument is not a tuple");
    return NULL;
  }

  len = PyTuple_GET_SIZE(args);
  if (len!=2) {
    PyErr_SetString(PyExc_TypeError,
		    "Pair.__new__ expects 2 arguments: (head, data)");
    return NULL;
  }
  
  self = (Expr *)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->pair = args;    
    self->hash = -1;
    Py_INCREF(self->pair);
  }
  return (PyObject *)self;
}

static long dict_hash(PyObject *d);
static long list_hash(PyObject *d);

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
  } else if (PyList_Check(item1)) {
    h = list_hash(item1);
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

  Code copied from Pyhton-2.5.1/Objects/setobject.c.
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
  hash(list) = hash(tuple(list))

  Code copied from Pyhton-2.5.1/Objects/tupleobject.c
*/
static long
list_hash(PyObject *o)
{
  PyListObject *v = (PyListObject *)o;
  register long x, y;
  register Py_ssize_t len = v->ob_size;
  register PyObject **p;
  long mult = 1000003L;
  x = 0x345678L;
  p = v->ob_item;
  while (--len >= 0) {
    y = PyObject_Hash(*p++);
    if (y == -1)
      return -1;
    x = (x ^ y) * mult;
    /* the cast might truncate len; that doesn't change hash stability */
    mult += (long)(82520L + len + len);
  }
  x += 97531L;
  if (x == -1)
    x = -2;
  return x;
}

/*
  expr = Expr(x, y)
  hash(expr) := hash(expr.as_lowlevel())
  if expr.pair is expr.as_lowlevel() and type(expr.data) is dict:
      hash(expr) := hash((expr.head, frozenset(expr.data.items())))
  else:
      hash(expr) := hash(expr.as_lowlevel())
 */
static long
Expr_hash(PyObject *self)
{
  Expr *o = (Expr *)self;
  PyObject *obj = NULL;
  if (o->hash!=-1)
    return o->hash;
  obj = PyObject_CallMethodObjArgs(self, str_as_lowlevel, NULL);
  if (obj==NULL)
    return -1;
  if (obj==o->pair)
    o->hash = tuple2_hash(PyTuple_GET_ITEM(o->pair, 0), PyTuple_GET_ITEM(o->pair, 1));
  else
    o->hash = PyObject_Hash(obj);
  Py_DECREF(obj);
  return o->hash;
}

static PyObject *
Expr_sethash(Expr *self, PyObject *args)
{
  long h = -1;
  if (PyArg_ParseTuple(args, "l", &h)==-1)
    return NULL;
  self->hash = h;
  Py_INCREF(Py_None);
  return Py_None;
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
    PyObject *data = PyTuple_GET_ITEM(self->pair, 1);
    if (Pair_CheckExact(data))
      return Expr_getis_writable((Expr*)data, closure);
    if (PyDict_CheckExact(data) || PyList_CheckExact(data)) {
      Py_RETURN_TRUE;
    }
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

/* Pickle support */
static PyObject *
Expr_reduce(Expr *self)
{
  /* version number of this pickle type. Increment if we need to
     change the format. Be sure to handle the old versions in
     sympycore.core._reconstruct. */
  const int version = 3;
  PyObject *mod = NULL;
  PyObject *ret = NULL;
  PyObject *obj = NULL;
  PyObject *cls = (PyObject *)self->ob_type;
  PyObject *typ = (PyObject *)cls->ob_type;
  PyObject *args = NULL;

  /* __reduce__ will return a tuple consisting of the following items:
     1) A callable object that will be called to create the initial
        version of the object:  sympycore.core._reconstruct.
     2) A tuple of arguments for the callable object:
           (version, state)
	If version==1 then
	  state = (cls, pair, hash)
	If version==2 or version==3 then
	  If args=type(cls).__getinitargs__(cls) succeeds then
  	    state = ((type(cls), args), pair, hash)
	  else
  	    state = (cls, pair, hash)
          For version==3, pair[0] is always HEAD instance
   */

  ret = PyTuple_New(2);
  if (ret == NULL) return NULL;

  mod = PyImport_ImportModule("sympycore.core");
  if (mod == NULL) return NULL;
  obj = PyObject_GetAttrString(mod, "_reconstruct");
  Py_DECREF(mod);
  if (obj == NULL) return NULL;

  PyTuple_SET_ITEM(ret, 0, obj);
  switch (version) {
  case 1:
    PyTuple_SET_ITEM(ret, 1,
		     Py_BuildValue("l(OOl)",
				   version,
				   cls,
				   self->pair,
				   self->hash));
    break;
  case 2:
  case 3:
    args = PyObject_CallMethodObjArgs(typ, str_getinitargs, cls, NULL);
    if (args==NULL) {
      PyErr_Clear();
      PyTuple_SET_ITEM(ret, 1,
		       Py_BuildValue("l(OOl)",
				     version,
				     cls,
				     self->pair,
				     self->hash));
    } else {
      PyTuple_SET_ITEM(ret, 1,
		       Py_BuildValue("l((ON)Ol)",
				     version,
				     typ, args,
				     self->pair,
				     self->hash));
    }
    break;
  default:
    printf("Expr.__reduce__: not implemented version = %d\n", version);
    PyErr_SetString(PyExc_NotImplementedError, "pickle state version");
    return NULL;
  }
  return ret;
}

/* Pickle support */
static PyObject *
Expr_as_lowlevel(Expr *self)
{
  PyObject *head = PyTuple_GET_ITEM(self->pair, 0);
  if (head==NUMBER || head==SYMBOL || head==SPECIAL) {
    PyObject *data = PyTuple_GET_ITEM(self->pair, 1);
    Py_INCREF(data);
    return data;
  }
  Py_INCREF(self->pair);
  return self->pair;
}

/* <Expr>.__nonzero__() == <Expr>.data.__nonzero__() 
   NOTE: __nonzero__ is active only for Expr subclasses.
*/
static PyObject*
Expr_nonzero(Expr *self) {
  PyObject* data = PyTuple_GET_ITEM(self->pair, 1);
  if (PyObject_IsTrue(data))
    Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

static PyObject*
Expr_nonzero2(Expr *self) {
  PyObject* head = PyTuple_GET_ITEM(self->pair, 0);
  PyObject* data = PyTuple_GET_ITEM(self->pair, 1);
  if (PyObject_IsTrue(head) || PyObject_IsTrue(data))
    Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

/*
  Return true if v and w type instances are comparable even when their
  types are different. Currently only exact types are checked.
 */
static int
check_comparable_types(PyObject *v, PyObject *w) {
  if (v->ob_type == w->ob_type)
    return 1;
  if (PyInt_CheckExact(v))
    return (PyLong_CheckExact(w) || PyFloat_CheckExact(w) || PyComplex_CheckExact(w));
  else if (PyLong_CheckExact(v))
    return (PyInt_CheckExact(w) || PyFloat_CheckExact(w) || PyComplex_CheckExact(w));
  else if (PyFloat_CheckExact(v))
    return (PyLong_CheckExact(w) || PyInt_CheckExact(w) || PyComplex_CheckExact(w));
  else if (PyComplex_CheckExact(v))
    return (PyLong_CheckExact(w) || PyFloat_CheckExact(w) || PyInt_CheckExact(w));
  /* XXX: enable when adding support to unicode strings.
  else if (PyString_CheckExact(v))
    return (PyString_CheckExact(w));
  */
  return 0;
}

static PyObject *
Expr_richcompare(PyObject *v, PyObject *w, int op)
{
  Expr *ve = (Expr *)v;
  Expr *we = (Expr *)w;
  if (Expr_Check(v) && v->ob_type == w->ob_type) {
    /* shortcut EQ and NE for speed: heads are singletons and data
       types are not comparable. */
    PyObject* vh = PyTuple_GET_ITEM(ve->pair, 0);
    PyObject* wh = PyTuple_GET_ITEM(we->pair, 0);
    PyObject* vd = PyTuple_GET_ITEM(ve->pair, 1);
    PyObject* wd = PyTuple_GET_ITEM(we->pair, 1);
    switch(op) {
    case Py_EQ:
      if (vh==wh) {
	if (vd==wd) {
	  Py_RETURN_TRUE;
	}
	if (check_comparable_types(vd, wd)) {
	  int r = PyObject_RichCompareBool(vd, wd, op);
	  if (r==-1) return NULL;
	  if (r) Py_RETURN_TRUE;
	  Py_RETURN_FALSE;
	}
	Py_RETURN_FALSE;
      }
      if (check_comparable_types(vd, wd))
	break;
      Py_RETURN_FALSE;
    case Py_NE:
      if (vh==wh) {
      	if (vd==wd) {
	  Py_RETURN_FALSE;
	}
	if (check_comparable_types(vd, wd)) {
	  int r = PyObject_RichCompareBool(vd, wd, op);
	  if (r==-1) return NULL;
	  if (r) Py_RETURN_TRUE;
	  Py_RETURN_FALSE;
	}
	Py_RETURN_TRUE;
      }
      if (check_comparable_types(vd, wd))
	break;
      Py_RETURN_TRUE;
    }
    /* do full comparison on pair tuples */
    return PyObject_RichCompare(ve->pair, we->pair, op);
  } 
  if (!Expr_Check(v)) {
    if (Expr_Check(w)) {
      PyObject* obj = PyObject_CallMethodObjArgs(w, str_as_lowlevel, NULL);
      int r;
      if (obj==NULL)
	return NULL;
      switch(op) {
      case Py_EQ:
	r = (check_comparable_types(v, obj)) ? PyObject_RichCompareBool(v, obj, op) : 0;
	break;
      case Py_NE:
	r = (check_comparable_types(v, obj)) ? PyObject_RichCompareBool(v, obj, op) : 1;
	break;
      default:
	r = PyObject_RichCompareBool(v, obj, op);
      }
      Py_DECREF(obj);
      if (r==-1) return NULL;
      if (r) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
    }
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (v->ob_type != w->ob_type) {
    PyObject* obj = PyObject_CallMethodObjArgs(v, str_as_lowlevel, NULL);
    int r;
    if (obj==NULL)
      return NULL;
      switch(op) {
      case Py_EQ:
	r = (check_comparable_types(obj, w)) ? PyObject_RichCompareBool(obj, w, op) : 0;
	break;
      case Py_NE:
	r = (check_comparable_types(obj, w)) ? PyObject_RichCompareBool(obj, w, op) : 1;
	break;  
      default:
	r = PyObject_RichCompareBool(obj, w, op);
      }
    Py_DECREF(obj);
    if (r==-1) return NULL;
    if (r) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
  }
  Py_INCREF(Py_NotImplemented);
  return Py_NotImplemented;
}

#define CHECK_MTH_ARGS(MTHNAME, NOFARGS) \
  if (!PyTuple_Check(args)) { \
    PyErr_SetString(PyExc_SystemError, \
		    "new style getargs format but argument is not a tuple"); \
    return NULL; \
  } else {\
    int nofargs = PyTuple_GET_SIZE(args);\
    if (nofargs!=(NOFARGS)) {\
      PyErr_SetObject(PyExc_TypeError, PyString_FromFormat(MTHNAME " takes %d argument (%d given)", NOFARGS, nofargs)); \
      return NULL;\
    }\
 }

#define CHECK_WRITABLE_DICTDATA(MTHNAME, SELF)	\
  if ((SELF)->hash!=-1) {\
    PyErr_SetString(PyExc_TypeError,\
		    MTHNAME ": data is not writable");\
    return NULL;\
  }\
  if (!PyDict_CheckExact(PyTuple_GET_ITEM((SELF)->pair, 1))) {\
    PyErr_SetString(PyExc_TypeError,\
		    MTHNAME ": data is not dict object");\
    return NULL;\
  }

#define CHECK_DICT_ARG(MTHNAME, OBJ) \
  if (!PyDict_CheckExact(OBJ)) { \
    PyErr_SetObject(PyExc_TypeError, \
	            PyString_FromFormat(MTHNAME\
		      ": argument must be dict object (got %s)",\
		      PyString_AsString(PyObject_Repr(PyObject_Type(OBJ))))); \
    return NULL; \
  }


static PyObject*
Expr_canonize_FACTORS(Expr *self) {
  PyObject *data = PyTuple_GET_ITEM(self->pair, 1);
  Py_ssize_t n = 0;
  PyObject *key = NULL;
  PyObject *value = NULL;
  PyObject *one = NULL;
  CHECK_DICT_ARG("Expr.canonize_FACTORS()", data);
  switch (PyDict_Size(data)) {
  case 0:
    return PyObject_GetAttrString((PyObject*)self, "one");
  case 1:
    PyDict_Next(data, &n, &key, &value);
    if (PyInt_CheckExact(value) && PyInt_AS_LONG(value)==1) {
      Py_INCREF(key);
      return key;
    }
    one = PyInt_FromLong(1);
    switch (PyObject_RichCompareBool(value, one, Py_EQ)) {
    case -1:
      Py_DECREF(one);
      return NULL;
    case 1: 
      Py_DECREF(one);
      Py_INCREF(key);
      return key;
    }
    Py_DECREF(one);
    one = PyObject_GetAttrString((PyObject*)self, "one");
    if (key==one || one==NULL) {
      return one;
    }
    switch (PyObject_RichCompareBool(key, one, Py_EQ)) {
    case -1:
      Py_DECREF(one);
      return NULL;
    case 1: 
      return one;
    }
    Py_DECREF(one);
  }
  Py_INCREF(self);
  return (PyObject*)self;
}

static PyObject*
Expr_canonize_TERMS(Expr *self) {
  PyObject *data = PyTuple_GET_ITEM(self->pair, 1);
  Py_ssize_t n = 0;
  PyObject *key = NULL;
  PyObject *value = NULL;
  PyObject *one = NULL;
  CHECK_DICT_ARG("Expr.canonize_TERMS()", data);
  switch (PyDict_Size(data)) {
  case 0:
    return PyObject_GetAttrString((PyObject*)self, "zero");
  case 1:
    PyDict_Next(data, &n, &key, &value);
    if (PyInt_CheckExact(value) && PyInt_AS_LONG(value)==1) {
      Py_INCREF(key);
      return key;
    }
    one = PyInt_FromLong(1);
    switch (PyObject_RichCompareBool(value, one, Py_EQ)) {
    case -1:
      Py_DECREF(one);
      return NULL;
    case 1: 
      Py_DECREF(one);
      Py_INCREF(key);
      return key;
    }
    Py_DECREF(one);
    one = PyObject_GetAttrString((PyObject*)self, "one");
    if (one==NULL)
      return NULL;
    if (key==one) {
      Py_INCREF(one);
      return Expr_new(((PyObject*)self)->ob_type, Py_BuildValue("(OO)", NUMBER, value), NULL);
    }
    switch (PyObject_RichCompareBool(key, one, Py_EQ)) {
    case -1:
      Py_DECREF(one);
      return NULL;
    case 1: 
      Py_INCREF(one);
      return Expr_new(((PyObject*)self)->ob_type, Py_BuildValue("(OO)", NUMBER, value), NULL);
    }
    Py_DECREF(one);
  }
  Py_INCREF(self);
  return (PyObject*)self;
}

static PyObject*
Expr_dict_add_dict(Expr *self, PyObject *args) {
  PyObject *sum = NULL;
  PyObject *obj = NULL;
  PyObject *data = PyTuple_GET_ITEM(self->pair, 1);
  PyObject *dict = NULL;
  PyObject *key = NULL;
  PyObject *value = NULL;
  Py_ssize_t pos = 0;
  CHECK_WRITABLE_DICTDATA("Expr._add_dict()", self);
  CHECK_MTH_ARGS("Expr._add_dict()", 1);
  dict = PyTuple_GET_ITEM(args, 0);
  CHECK_DICT_ARG("Expr._add_dict()", dict);
  while (PyDict_Next(dict, &pos, &key, &value)) {
    obj = PyDict_GetItem(data, key);
    if (obj==NULL) { 
      if (PyDict_SetItem(data, key, value)==-1)
	return NULL;
    } else {
      if ((sum = PyNumber_Add(obj, value))==NULL)
	return NULL;
      if (PyInt_CheckExact(sum) ? PyInt_AS_LONG(sum) : PyObject_IsTrue(sum)) {
	if (PyDict_SetItem(data, key, sum)==-1)
	  return NULL;
      } else {
	if (PyDict_DelItem(data, key)==-1)
	  return NULL;
      }
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject*
Expr_dict_sub_dict(Expr *self, PyObject *args) {
  PyObject *sum = NULL;
  PyObject *obj = NULL;
  PyObject *data = PyTuple_GET_ITEM(self->pair, 1);
  PyObject *dict = NULL;
  PyObject *key = NULL;
  PyObject *value = NULL;
  Py_ssize_t pos = 0;
  CHECK_WRITABLE_DICTDATA("Expr._sub_dict()", self);
  CHECK_MTH_ARGS("Expr._sub_dict()", 1);
  dict = PyTuple_GET_ITEM(args, 0);
  CHECK_DICT_ARG("Expr._sub_dict()", dict);
  while (PyDict_Next(dict, &pos, &key, &value)) {
    obj = PyDict_GetItem(data, key);
    if (obj==NULL) { 
      if (PyDict_SetItem(data, key, PyNumber_Negative(value))==-1)
	return NULL;
    } else {
      if ((sum = PyNumber_Subtract(obj, value))==NULL)
	return NULL;
      if (PyInt_CheckExact(sum) ? PyInt_AS_LONG(sum) : PyObject_IsTrue(sum)) {
	if (PyDict_SetItem(data, key, sum)==-1)
	  return NULL;
      } else {
	if (PyDict_DelItem(data, key)==-1)
	  return NULL;
      }
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject*
Expr_dict_add_dict2(Expr *self, PyObject *args) {
  PyObject *sum = NULL;
  PyObject *obj = NULL;
  PyObject *data = PyTuple_GET_ITEM(self->pair, 1);
  PyObject *dict = NULL;
  PyObject *key = NULL;
  PyObject *value = NULL;
  PyObject *coeff = NULL;
  PyObject *tmp = NULL;
  Py_ssize_t pos = 0;
  CHECK_WRITABLE_DICTDATA("Expr._add_dict2()", self);
  CHECK_MTH_ARGS("Expr._add_dict2()", 2);
  dict = PyTuple_GET_ITEM(args, 0);
  CHECK_DICT_ARG("Expr._add_dict2()", dict);
  coeff = PyTuple_GET_ITEM(args, 1);
  while (PyDict_Next(dict, &pos, &key, &value)) {
    tmp = PyNumber_Multiply(value, coeff);
    obj = PyDict_GetItem(data, key);
    if (obj==NULL) {
      if (PyDict_SetItem(data, key, tmp)==-1)
	return NULL;
    } else {
      if ((sum = PyNumber_Add(obj, tmp))==NULL)
	return NULL;
      if (PyInt_CheckExact(sum) ? PyInt_AS_LONG(sum) : PyObject_IsTrue(sum)) {
	if (PyDict_SetItem(data, key, sum)==-1)
	  return NULL;
      } else {
	if (PyDict_DelItem(data, key)==-1)
	  return NULL;
      }
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject*
Expr_dict_add_dict3(Expr *self, PyObject *args) {
  PyObject *sum = NULL;
  PyObject *obj = NULL;
  PyObject *data = PyTuple_GET_ITEM(self->pair, 1);
  PyObject *dict = NULL;
  PyObject *key = NULL;
  PyObject *value = NULL;
  Py_ssize_t pos = 0;
  PyTypeObject *type = ((PyObject*)self)->ob_type;
  PyObject *result = NULL;
  PyObject *tmp = NULL;
  CHECK_WRITABLE_DICTDATA("Expr._add_dict3()", self);
  CHECK_MTH_ARGS("Expr._add_dict3()", 1);
  dict = PyTuple_GET_ITEM(args, 0);
  CHECK_DICT_ARG("Expr._add_dict3()", dict);
  while (PyDict_Next(dict, &pos, &key, &value)) {
    obj = PyDict_GetItem(data, key);
    if (obj==NULL) { 
      if (PyDict_SetItem(data, key, value)==-1)
	return NULL;
    } else {
      if ((sum = PyNumber_Add(obj, value))==NULL)
	return NULL;
      if (sum->ob_type==type && PyTuple_GET_ITEM(((Expr*)sum)->pair, 0)==NUMBER) {
	tmp = PyTuple_GET_ITEM(((Expr*)sum)->pair, 1);
	Py_DECREF(sum);
	sum = tmp;
      }
      if (PyInt_CheckExact(sum) ? PyInt_AS_LONG(sum) : PyObject_IsTrue(sum)) {
	if (key->ob_type==type && PyTuple_GET_ITEM(((Expr*)key)->pair, 0)==NUMBER) {
	  if (result==NULL)
	    tmp = PyObject_CallMethodObjArgs((PyObject*)self,
					     str_handle_numeric_item,
					     Py_None,
					     key,
					     sum,
					     NULL
					     );
	  else
	    tmp = PyObject_CallMethodObjArgs((PyObject*)self,
					     str_handle_numeric_item,
					     result,
					     key,
					     sum,
					     NULL
					     );
	  if (tmp==NULL) // XXX: cleanup
	    return NULL;
	  result = tmp;
	} else if (PyDict_SetItem(data, key, sum)==-1)
	  return NULL;
      } else {
	if (PyDict_DelItem(data, key)==-1)
	  return NULL;
      }
    }
  }
  if (result==NULL) {
    Py_INCREF(Py_None);
    return Py_None;
  }
  return result;
}

/*
  If Expr.data is dictionary then add to it non-zero value inplace.
 */
static PyObject *
Expr_dict_add_item(Expr *self, PyObject *args) {
  PyObject *sum = NULL;
  PyObject *obj = NULL;
  PyObject *d = PyTuple_GET_ITEM(self->pair, 1);
  PyObject *item_key = NULL;
  PyObject *item_value = NULL;
  CHECK_WRITABLE_DICTDATA("Expr._add_item()", self);
  CHECK_MTH_ARGS("Expr._add_item()", 2);
  item_key = PyTuple_GET_ITEM(args, 0);
  item_value = PyTuple_GET_ITEM(args, 1);
  obj = PyDict_GetItem(d, item_key);
  if (obj==NULL) { 
    if (PyDict_SetItem(d, item_key, item_value)==-1)
      return NULL;
  } else {
    if ((sum = PyNumber_Add(obj, item_value))==NULL)
      return NULL;
    if (PyInt_CheckExact(sum) ? PyInt_AS_LONG(sum) : PyObject_IsTrue(sum)) {
      if (PyDict_SetItem(d, item_key, sum)==-1)
	return NULL;
    } else {
      if (PyDict_DelItem(d, item_key)==-1)
	return NULL;
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

/*
  If Expr.data is dictionary then subtract from it non-zero value inplace.
 */
static PyObject *
Expr_dict_sub_item(Expr *self, PyObject *args) {
  PyObject *sum = NULL;
  PyObject *obj = NULL;
  PyObject *d = PyTuple_GET_ITEM(self->pair, 1);
  PyObject *item_key = NULL;
  PyObject *item_value = NULL;
  CHECK_WRITABLE_DICTDATA("Expr._sub_item()", self);
  CHECK_MTH_ARGS("Expr._sub_item()", 2);
  item_key = PyTuple_GET_ITEM(args, 0);
  item_value = PyTuple_GET_ITEM(args, 1);
  obj = PyDict_GetItem(d, item_key);
  if (obj==NULL) { 
    if (PyDict_SetItem(d, item_key, PyNumber_Negative(item_value))==-1)
      return NULL;
  } else {
    if ((sum = PyNumber_Subtract(obj, item_value))==NULL)
      return NULL;
    if (PyInt_CheckExact(sum) ? PyInt_AS_LONG(sum) : PyObject_IsTrue(sum)) {
      if (PyDict_SetItem(d, item_key, sum)==-1)
	return NULL;
    } else {
      if (PyDict_DelItem(d, item_key)==-1)
	return NULL;
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static Py_ssize_t
Pairlength(Expr *self)
{
  return ((PyTupleObject*)(self->pair))->ob_size;
}

static PyObject *
Pairitem(register Expr *self, register Py_ssize_t i)
{
  if (i < 0 || i >= ((PyTupleObject*)(self->pair))->ob_size) {
    PyErr_SetString(PyExc_IndexError, "Pair index out of range");
    return NULL;
  }
  Py_INCREF(((PyTupleObject*)(self->pair))->ob_item[i]);
  return ((PyTupleObject*)(self->pair))->ob_item[i];
}

static PyObject *init_module(PyObject *self, PyObject *args)
{
  if (NUMBER==NULL)
    {
      PyObject* m = PyImport_ImportModule("sympycore.heads");
      if (m == NULL)
	return NULL;
      NUMBER = PyObject_GetAttrString(m, "NUMBER");
      if (NUMBER==NULL) {
	Py_DECREF(m);
	return NULL;
      }
      SYMBOL = PyObject_GetAttrString(m, "SYMBOL");
      if (SYMBOL==NULL) {
	Py_DECREF(m);
	return NULL;
      }
      SPECIAL = PyObject_GetAttrString(m, "SPECIAL");
      if (SPECIAL==NULL) {
	Py_DECREF(m);
	return NULL;
      }
      Py_DECREF(m);
    }
  return Py_BuildValue("");
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

static PyMethodDef Expr_methods[] = {
  {"__reduce__", (PyCFunction)Expr_reduce, METH_VARARGS, NULL},
  {"__nonzero__", (PyCFunction)Expr_nonzero, METH_VARARGS, NULL},
  {"__nonzero2__", (PyCFunction)Expr_nonzero2, METH_VARARGS, NULL},
  {"_sethash", (PyCFunction)Expr_sethash, METH_VARARGS, NULL},
  {"as_lowlevel", (PyCFunction)Expr_as_lowlevel, METH_VARARGS, NULL},
  {"_add_item", (PyCFunction)Expr_dict_add_item, METH_VARARGS, NULL},
  {"_sub_item", (PyCFunction)Expr_dict_sub_item, METH_VARARGS, NULL},
  {"_add_dict", (PyCFunction)Expr_dict_add_dict, METH_VARARGS, NULL},
  {"_sub_dict", (PyCFunction)Expr_dict_sub_dict, METH_VARARGS, NULL},
  {"_add_dict2", (PyCFunction)Expr_dict_add_dict2, METH_VARARGS, NULL},
  {"_add_dict3", (PyCFunction)Expr_dict_add_dict3, METH_VARARGS, NULL},
  {"canonize_FACTORS", (PyCFunction)Expr_canonize_FACTORS, METH_VARARGS, NULL},
  {"canonize_TERMS", (PyCFunction)Expr_canonize_TERMS, METH_VARARGS, NULL},
  {NULL, NULL}           /* sentinel */
};

static PyTypeObject ExprType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "Expr",                    /*tp_name*/
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
  Expr_richcompare,	     /* tp_richcompare */
  0,	                     /* tp_weaklistoffset */
  0,	                     /* tp_iter */
  0,	                     /* tp_iternext */
  Expr_methods,              /* tp_methods */
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

static PySequenceMethods Pair_as_sequence = {
  (lenfunc)Pairlength,       /* sq_length */
  0,                         /* sq_concat */
  0,                         /* sq_repeat */
  (ssizeargfunc)Pairitem,    /* sq_item */
  0,                         /* sq_slice */
  0,                         /* sq_ass_item */
  0,                         /* sq_ass_slice */
  0,                         /* sq_contains */
};


static PyTypeObject PairType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "Pair",                    /*tp_name*/
  sizeof(Expr),              /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  0,                         /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  &Pair_as_sequence,         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,                         /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
  0,                         /* tp_doc */
  0,                         /* tp_traverse */
  0,                         /* tp_clear */
  0,	                     /* tp_richcompare */
  0,	                     /* tp_weaklistoffset */
  0,	                     /* tp_iter */
  0,	                     /* tp_iternext */
  0,                         /* tp_methods */
  0,                         /* tp_members */
  0,                         /* tp_getset */
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
  {"init_module",  init_module, METH_VARARGS, "Initialize module."},
  {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initexpr_ext(void) 
{
  PyObject* m = NULL;
  NUMBER = SYMBOL = SPECIAL = NULL;

  if (PyType_Ready(&ExprType) < 0)
    return;

  PairType.tp_base = &ExprType;
  if (PyType_Ready(&PairType) < 0)
    return;

  str_as_lowlevel = PyString_FromString("as_lowlevel");
  if (str_as_lowlevel==NULL)
    return;
  str_convert = PyString_FromString("convert");
  if (str_convert==NULL)
    return;
  str_handle_numeric_item = PyString_FromString("handle_numeric_item");
  if (str_handle_numeric_item==NULL)
    return;
  str_getinitargs = PyString_FromString("__getinitargs__");
  if (str_getinitargs==NULL)
    return;
  m = Py_InitModule3("expr_ext", module_methods, "Provides extension type Expr.");
  
  if (m == NULL)
    return;

  Py_INCREF(&ExprType);
  PyModule_AddObject(m, "Expr", (PyObject *)&ExprType);

  Py_INCREF(&PairType);
  PyModule_AddObject(m, "Pair", (PyObject *)&PairType);
}
