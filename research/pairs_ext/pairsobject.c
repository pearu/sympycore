/*
  Implementation of Pairs object type.

  Author: Pearu Peterson
  Created: March 2008
 */

#ifdef __cplusplus
extern "C" {
#endif
#define NO_USE_JUST_CHEAT_EMACS }

#include "Python.h"
#include "pairsobject.h"

/* This must be >= 1. */
#define PERTURB_SHIFT 5

/* Object used as dummy key to fill deleted entries */
static PyObject *dummy = NULL; /* Initialized by first call to make_new_pairs() */

/* Reuse scheme to save calls to malloc, free, and memset */
#define MAXFREEPAIRS 80
static PairsObject *free_pairs[MAXFREEPAIRS];
static int num_free_pairs = 0;

/*
The basic lookup function used by all operations.  This is based on
Algorithm D from Knuth Vol. 3, Sec. 6.4.  Open addressing is preferred
over chaining since the link overhead for chaining would be
substantial (100% with typical malloc overhead).

The initial probe index is computed as hash mod the table
size. Subsequent probe indices are computed as explained in
Objects/dictobject.c.

All arithmetic on hash should ignore overflow.

Pairs_look_lhs function can return NULL if the rich comparison returns
an error.

TODO: Pairs entry lhs part is most probably an instance of class that
uses Pairs or arbitrary python object as data attribute (in parallel
with head attribute). This condition can be used for avoiding calling
PyObject_RichCompare that otherwise would be more useful for returning
relational instances.

*/

static PairsEntry *
pairs_look_lhs(PairsObject *o, PyObject *lhs, register long hash)
{
  register Py_ssize_t i;
  register size_t perturb;
  register PairsEntry *freeslot;
  register size_t mask = o->mask;
  PairsEntry *table = o->table;
  register PairsEntry *entry;
  register int cmp;
  PyObject *startlhs;

  i = hash & mask;
  entry = &table[i];
  if (entry->lhs == NULL || entry->lhs == lhs)
    return entry;

  if (entry->lhs == dummy)
    freeslot = entry;
  else {
    if (entry->hash == hash) {
      startlhs = entry->lhs;
      cmp = PyObject_RichCompareBool(startlhs, lhs, Py_EQ);
      if (cmp < 0)
	return NULL;
      if (table == o->table && entry->lhs == startlhs) {
	if (cmp > 0)
	  return entry;
      }
      else {
	/* The compare did major nasty stuff to the
	 * set:  start over.
	 */
	return pairs_look_lhs(o, lhs, hash);
      }
    }
    freeslot = NULL;
  }
  
  /* In the loop, lhs == dummy is by far (factor of 100s) the
     least likely outcome, so test for that last. */
  for (perturb = hash; ; perturb >>= PERTURB_SHIFT) {
    i = (i << 2) + i + perturb + 1;
    entry = &table[i & mask];
    if (entry->lhs == NULL) {
      if (freeslot != NULL)
	entry = freeslot;
      break;
    }
    if (entry->lhs == lhs)
      break;
    if (entry->hash == hash && entry->lhs != dummy) {
      startlhs = entry->lhs;
      cmp = PyObject_RichCompareBool(startlhs, lhs, Py_EQ);
      if (cmp < 0)
	return NULL;
      if (table == o->table && entry->lhs == startlhs) {
	if (cmp > 0)
	  break;
      }
      else {
	/* The compare did major nasty stuff to the Pairs: start over.
	 */
	return pairs_look_lhs(o, lhs, hash);
      }
    }
    else if (entry->lhs == dummy && freeslot == NULL)
      freeslot = entry;
  }
  return entry;
}

/*
Internal routine to insert a new (lhs,rhs) pair into the table.
Used both by the internal resize routine and by the public insert routine.
Eats a reference to lhs and one to rhs.
Returns -1 if an error occurred, or 0 on success.
*/
static int
pairs_insert(register PairsObject *o, PyObject *lhs, long hash, PyObject *rhs)
{
  PyObject *old_rhs;
  register PairsEntry *entry;
  typedef PairsEntry *(*lookupfunc)(PairsObject *, PyObject *, long);

  assert(o->lookup != NULL);
  entry = o->lookup(o, lhs, hash);
  if (entry == NULL) {
    Py_DECREF(lhs);
    Py_DECREF(rhs);
    return -1;
  }
  if (entry->rhs != NULL) {
    old_rhs = entry->rhs;
    entry->rhs = rhs;
    Py_DECREF(old_rhs); /* which **CAN** re-enter */
    Py_DECREF(lhs);
  }
  else {
    if (entry->lhs == NULL)
      o->fill++;
    else {
      assert(entry->lhs == dummy);
      Py_DECREF(dummy);
    }
    entry->lhs = lhs;
    entry->hash = (Py_ssize_t)hash;
    entry->rhs = rhs;
    o->used++;
  }
  return 0;
}

/*
Internal routine used by pairs_resize() to insert an item which is
known to be absent from the pairs.  This routine also assumes that
the pairs contains no deleted entries.  Besides the performance benefit,
using pairs_insert() in pairs_resize() is dangerous (SF bug #1456209).
Note that no refcounts are changed by this routine; if needed, the caller
is responsible for incref'ing `lhs` and `rhs`.
*/
static void
pairs_insert_clean(register PairsObject *o, PyObject *lhs, long hash,
		   PyObject *rhs)
{
  register size_t i;
  register size_t perturb;
  register size_t mask = (size_t)o->mask;
  PairsEntry *table = o->table;
  register PairsEntry *entry;

  i = hash & mask;
  entry = &table[i];
  for (perturb = hash; entry->lhs != NULL; perturb >>= PERTURB_SHIFT) {
    i = (i << 2) + i + perturb + 1;
    entry = &table[i & mask];
  }
  assert(entry->rhs == NULL);
  o->fill++;
  entry->lhs = lhs;
  entry->hash = (Py_ssize_t)hash;
  entry->rhs = rhs;
  o->used++;
}

/*
Restructure the table by allocating a new table and reinserting all
items again.  When entries have been deleted, the new table may
actually be smaller than the old one.
*/
static int
pairs_table_resize(PairsObject *o, Py_ssize_t minused)
{
  Py_ssize_t newsize;
  PairsEntry *oldtable, *newtable, *entry;
  Py_ssize_t i;
  int is_oldtable_malloced;
  PairsEntry small_copy[Pairs_MINSIZE];

  assert(minused >= 0);

  /* Find the smallest table size > minused. */
  for (newsize = Pairs_MINSIZE;
       newsize <= minused && newsize > 0;
       newsize <<= 1)
    ;
  if (newsize <= 0) {
    PyErr_NoMemory();
    return -1;
  }

  /* Get space for a new table. */
  oldtable = o->table;
  assert(oldtable != NULL);
  is_oldtable_malloced = oldtable != o->smalltable;

  if (newsize == Pairs_MINSIZE) {
    /* A large table is shrinking, or we can't get any smaller. */
    newtable = o->smalltable;
    if (newtable == oldtable) {
      if (o->fill == o->used) {
	/* No dummies, so no point doing anything. */
	return 0;
      }
      /* We're not going to resize it, but rebuild the table anyway to
	 purge old dummy entries.  Subtle: This is *necessary* if
	 fill==size, as pairs_look_lhs needs at least one virgin slot
	 to terminate failing searches.  If fill < size, it's merely
	 desirable, as dummies slow searches. */
      assert(o->fill > o->used);
      memcpy(small_copy, oldtable, sizeof(small_copy));
      oldtable = small_copy;
    }
  }
  else {
    newtable = PyMem_NEW(PairsEntry, newsize);
    if (newtable == NULL) {
      PyErr_NoMemory();
      return -1;
    }
  }

  /* Make the pairs empty, using the new table. */
  assert(newtable != oldtable);
  o->table = newtable;
  o->mask = newsize - 1;
  memset(newtable, 0, sizeof(PairsEntry) * newsize);
  o->used = 0;
  i = o->fill;
  o->fill = 0;


  /* Copy the data over; this is refcount-neutral for active entries;
     dummy entries aren't copied over, of course */
  for (entry = oldtable; i > 0; entry++) {
    if (entry->rhs != NULL) {     /* active entry */
      --i;
      pairs_insert_clean(o, entry->lhs, (long)entry->hash, entry->rhs);
    }
    else if (entry->lhs != NULL) {  /* dummy entry */
      --i;
      assert(entry->lhs == dummy);
      Py_DECREF(entry->lhs);
    }
    /* else lhs == rhs == NULL:  nothing to do */
  }

  if (is_oldtable_malloced)
    PyMem_DEL(oldtable);
  return 0;
}


#ifdef NOTREADYTOCOMPILE
PyTypeObject Pairs_Type = {
        PyObject_HEAD_INIT(&PyType_Type)
        0,
        "Pairs",
        sizeof(PairsObject),
        0,
        (destructor)pairs_dealloc,               /* tp_dealloc */
        (printfunc)pairs_print,                  /* tp_print */
        0,                                      /* tp_getattr */
        0,                                      /* tp_setattr */
        0, /*(cmpfunc)pairs_compare,*/                  /* tp_compare */
        (reprfunc)pairs_repr,                    /* tp_repr */
        0,                                      /* tp_as_number */
        &pairs_as_sequence,                      /* tp_as_sequence */
        &pairs_as_mapping,                       /* tp_as_mapping */
        pairs_hash,                            /* tp_hash */
        0,                                      /* tp_call */
        0,                                      /* tp_str */
        PyObject_GenericGetAttr,                /* tp_getattro */
        0,                                      /* tp_setattro */
        0,                                      /* tp_as_buffer */
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
                Py_TPFLAGS_BASETYPE,            /* tp_flags */
        pairs_doc,                         /* tp_doc */
        pairs_traverse,                          /* tp_traverse */
        pairs_tp_clear,                          /* tp_clear */
        0, /*pairs_richcompare,*/                       /* tp_richcompare */
        0,                                      /* tp_weaklistoffset */
        (getiterfunc)pairs_iter,                 /* tp_iter */
        0,                                      /* tp_iternext */
        0, /*mapp_methods,*/                           /* tp_methods */
        0,                                      /* tp_members */
        0,                                      /* tp_getset */
        0,                                      /* tp_base */
        0,                                      /* tp_dict */
        0,                                      /* tp_descr_get */
        0,                                      /* tp_descr_set */
        0,                                      /* tp_dictoffset */
        pairs_init,                              /* tp_init */
        PyType_GenericAlloc,                    /* tp_alloc */
        pairs_new,                               /* tp_new */
        PyObject_GC_Del,                        /* tp_free */
};
#endif







#ifdef __cplusplus
}
#endif
