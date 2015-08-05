# Introduction #

SympyCore subpackages tend to have very similar code structure and it
might be wise to write down few suggestions how to organize the
content of a newly created subpackage.

## General style guide ##

  * Use CamelCase for all class names except if they represent mathematical functions such as `sin`, `cos`, etc.
  * Use relative imports for importing objects from other modules. Use absolute import from future if necessary.
  * Avoid importing other `sympycore` subpackages unless it is absolutely necessary. Use `classes.ClassName` instead of importing `ClassName` explicitly from a subpackage that defines it. Importing subpackages explicitly is necessary only when deriving a class from the one that is defined in a subpackage.
  * Use singletons where appropiate. There are a number of preconstructed instances such as `one`, `zero`, `oo`, `pi`, `I`, `E`, etc that are saved as attributes of the `objects` instance.
  * Use CamelCase for public functions such as Expand, Diff, etc for consistency ???.

## General structure guide ##

XXX: describe sympycore package structure.

## Relevant issues ##

  * [sympycore issue 8](http://code.google.com/p/sympycore/issues/detail?id=8) - Naming classes, functions, methods, etc.
  * [sympycore issue 10](http://code.google.com/p/sympycore/issues/detail?id=10) - Global module organization
  * [sympycore issue 19](http://code.google.com/p/sympycore/issues/detail?id=19) - Rename Minus to Difference
  * [sympycore issue 20](http://code.google.com/p/sympycore/issues/detail?id=20) - Important functions.
  * [sympy issue 651](http://code.google.com/p/sympy/issues/detail?id=651) - Syntax policy.