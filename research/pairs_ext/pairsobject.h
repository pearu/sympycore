/*
  PairsObject - defines python Pairs type object that holds pairs
  (lhs, rhs). Here lhs is treated as a dictionary key and rhs as a
  dictionary value. Different from dictionary, Pairs defines hash
  value so that Pairs instances can be used as dictionary or Pairs
  keys. When created, Pairs is a mutable object until its hash value
  is computed, then it becomes immutable. In a way, Pairs is a
  combination of a dictionary and frozenset types. This allows reusing
  dictionary and frozenset code in many places, especially the lookup
  methods.

  Different from dictionary and frozenset, Pairs does not define
  sequence protocol. Instead it provides methods to retrive Pairs
  items. The reason for not defining sequence protocol for Pairs is to
  prevent numpy.array to treat a Pairs instance as a sequence.

  Author: Pearu Peterson
  Created: March 2008
 */

#ifndef PAIRSOBJECT_H
#define PAIRSOBJECT_H
#ifdef __cplusplus
extern "C" {
#endif
#define NO_USE_JUST_CHEAT_EMACS }

/*
There are three kinds of slots in the table:

1. Unused:  lhs == NULL
   Does not hold an active (lhs, rhs) pair now and never did.  Unused can
   transition to Active upon lhs insertion.  This is the only case in which
   lhs is NULL, and is each slot's initial state.

2. Active:  lhs != NULL and lhs != dummy
   Holds an active (lhs, rhs) pair.  Active can transition to Dummy upon
   key deletion.  This is the only case in which rhs != NULL.

3. Dummy:   lhs == dummy
   Previously held an active (lhs, rhs) pair, but that was deleted and an
   active pair has not yet overwritten the slot.  Dummy can transition to
   Active upon key insertion.  Dummy slots cannot be made Unused again
   (cannot have lhs set to NULL), else the probe sequence in case of
   collision would have no way to know they were once active.

   XXX: is this relevant for Pairs?
*/

/* Pairs_MINSIZE is the minimum size of a Pairs.  This many slots are
   allocated directly in the Pairs object (in the ma_smalltable
   member).  It must be a power of 2, and at least 4.  8 allows Pairs
   with no more than 5 active entries to live in ma_smalltable (and so
   avoid an additional malloc).

   XXX: test also sizes 16, 32 as "usually-small instance Pairs"
   argument may not be valid for sums. Though it may be valid for
   products in a sum.
 */

#define Pairs_MINSIZE 8

typedef struct {
  Py_ssize_t hash; /* cached hash of lhs */
  /*
    The hash of (lhs, rhs) is needed when computing the hash of
    Pairs. At the moment of doing so, Pairs becomes immutable which
    means the all the rhs parts of its entries will be fixed. Until
    then the rhs parts may change. Hence caching the hash of the rhs
    part does not make sense.
   */
  PyObject *lhs;
  PyObject *rhs;
} PairsEntry;

typedef struct _pairsobject PairsObject;
struct _pairsobject {
  PyObject_HEAD
  
  Py_ssize_t fill;  /* # Active + # Dummy */
  Py_ssize_t used;  /* # Active */
  
  /* The table contains mask + 1 slots, and that's a power of 2.
     We store the mask instead of the size because the mask is
     more frequently needed.
  */
  Py_ssize_t mask;
  
  /* table points to smalltable for small tables, else to
     additional malloc'ed memory.  table is never NULL!  This
     rule saves repeated runtime null-tests.
  */
  PairsEntry *table;
  PairsEntry *(*lookup)(PairsObject *so, PyObject *lhs, long hash);
  PairsEntry smalltable[Pairs_MINSIZE];
  
  long hash;              /* when -1 then hash is not computed */
  PyObject *weakreflist;  /* List of weak references */
};

PyAPI_DATA(PyTypeObject) Pairs_Type;

#define Pairs_Check(op) PyObject_TypeCheck(op, &Pairs_Type)
#define Pairs_CheckExact(op) ((op)->ob_type == &Pairs_Type)

#ifdef __cplusplus
}
#endif
#endif /* !PAIRSOBJECT_H */

