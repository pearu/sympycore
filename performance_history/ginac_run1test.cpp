/*
  Compile: c++ ginac_run1test.cpp -o app -lcln -lginac
  Run: ./app

Example:

$ ./app 
12/5*z+2*y+3/2*x
161290


  Created: July 2008 by Pearu Peterson
*/

#include <iostream>
#include <ginac/ginac.h>
#include <time.h>

using namespace std;
using namespace GiNaC;

#define N 50000

int main()
{
  symbol x("x"), y("y"), z("z");
  numeric a(1,2), b(2,3), c(4,5); 
  ex r;
  int i=N;
  clock_t elapsed;

  elapsed = clock();
  while(i--)
    r = 3*(a*x + b*y + c*z);
  elapsed = clock() - elapsed;

  if (!elapsed)
    cerr << "INCREASE THE NUMBER OF ITERATIONS" << endl;

  cout << r << endl;
  cout << double(N*CLOCKS_PER_SEC)/(elapsed) << endl;
  return 0;
}
