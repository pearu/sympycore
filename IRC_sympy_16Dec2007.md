
```
(04:21:13 PM) ondrej: hi pearu
(04:23:25 PM) ondrej: just got home from mountains
(04:30:01 PM) pearu: hi, nice to meet you here
(04:30:20 PM) ondrej: I didn't get - why cannot you use a direct instance?
(04:30:24 PM) ondrej: (in IS)
(04:31:20 PM) pearu: this is because it is not always possible to import classes from other modules when there is a risk of getting circular imports
(04:31:48 PM) pearu: isinstance(obj, classes.clsname) could be an option
(04:32:19 PM) ondrej: yes, that's what I thought
(04:32:25 PM) pearu: that might be actually optimal
(04:32:52 PM) ondrej: but I think IS will be slower, than is_Add (that is currently in sympycore)
(04:33:18 PM) ondrej: do you have some idea how much it is slower?
(04:33:39 PM) ondrej: (one more function call) I don't have a feeling for these things in python
(04:33:44 PM) pearu: yes, that wil be always be so, I would estimate not more than 6-7times
(04:34:01 PM) ondrej: 7 times? that's a lot
(04:35:01 PM) pearu: calling __getattribute__ (that includes attribute search) plus isinstance call is 8x slower, using IS approach would be faster
(04:35:22 PM) pearu: when IS=isinstance, then it will be 2x slower
(04:35:46 PM) pearu: but I need to test, these estimates can be wrong
(04:36:15 PM) ondrej: 8x slower than using is_Add ?
(04:36:49 PM) ondrej: so the isinstance is actually pretty fast, only is_Add is faster, right?
(04:37:05 PM) pearu: yes, but note that this estimate is about only checking types
(04:37:33 PM) pearu: however, in real apps time spent in checking types can be insignificant
(04:37:48 PM) ondrej: then my proposed docstring is bad - the IS will always be slower, than isinstance
(04:38:08 PM) ondrej: so what is the point of IS than? If it's slower than both isinstance and is_Add
(04:38:13 PM) pearu: nope, when IS=isinstance, they have the same speed
(04:38:22 PM) ondrej: oh I see.
(04:38:28 PM) ondrej: ok, then everything is ok
(04:38:59 PM) ondrej: let's use IS then, so that we can switch it easily anytime we want
(04:39:06 PM) pearu: but this is again at the cost of accessing classes attributes, using is_Add is always the fastest
(04:40:03 PM) ondrej: I think the only way to decide this is to test it in sympycore, how much it slows things down
(04:40:18 PM) ondrej: if it's negligible, we don't have to talk about it
(04:40:19 PM) pearu: yes, I agree, I'll certainly do that
(04:40:43 PM) ondrej: (but if it's negligible, the whole thing with is_Add was not necessary imho, we could use isinstance)
(04:41:30 PM) ondrej: what do you think are the biggest speedups in sympycore? Definitely the fast Add and Mul, and then comparisons imho
(04:41:31 PM) pearu: the isinstance(obj, classes.Add) has only one problem: it reads long
(04:41:40 PM) ondrej: agree
(04:43:01 PM) pearu: but in long term (when the code base will be stable) I think isinstance is also fine, in fact, while working with the functions, isinstance is safest at the moment
(04:43:30 PM) ondrej: yep, I like the idea of having is_Add just for a few classes
(04:45:11 PM) pearu: when talking about speedups, then comparions play a big role as it is used all the time (dictionary lookups, equality checks) and pretty much everywhere
(04:45:48 PM) ondrej: I think so too
(04:46:24 PM) pearu: in sympycore we had to sacrifice __lt__, etc methods for fast comparison so that they cannot be used to generate relational instances, Less, etc must be used directly
(04:46:55 PM) ondrej: is __lt__ some particularly fast?
(04:47:12 PM) ondrej: or why you couldn't use Less for comparisons
(04:47:40 PM) ondrej: (so that you could use list sort, or something?)
(04:48:07 PM) pearu: no, but as soon as a class defines __lt__ method, it will be used by Python for comparisons, the __cmp__ method will be just ignored
(04:48:54 PM) ondrej: but why do you need to compare using < ?
(04:49:11 PM) pearu: for sorting, for instance
(04:51:18 PM) ondrej: yeah.
(04:51:31 PM) pearu: but on the other hand, sorting is used only in generating str values, so it is not a big problem
(04:51:52 PM) pearu: may be it was when Add used to use sorting..
(04:52:20 PM) ondrej: so when you type x+y and y+x, is it stored internally differently?
(04:52:50 PM) pearu: they are stored internally as dictionaries {x:1, y:1}, so, they are the same
(04:52:58 PM) ondrej: ah, I forgot
(04:53:19 PM) ondrej: but then the x and y need to have hashes working
(04:53:52 PM) pearu: yes, hashing is another thing that affects performance noticable
(04:54:07 PM) ondrej: the oldcore used to use hashes.
(04:54:58 PM) ondrej: so comparisons is in fact done using hashes, right?
(04:55:47 PM) pearu: I believe that using builtin hash methods is faster, like Symbol uses str.__hash__, Add uses frozenset.__hash__, etc
(04:56:20 PM) ondrej: yes, the builtin hash is faster
(04:56:31 PM) ondrej: how do you calculate hash of (x+y)**2?
(04:56:49 PM) ondrej: I used to have issues with this.
(04:56:55 PM) pearu: hashes are not guaranteed to be unique enough
(04:57:02 PM) ondrej: ok then.
(04:57:13 PM) ondrej: but it fails then sometimes, doesn't it?
(04:57:49 PM) ondrej: (the builtin hash is unique enough for our purposes imho)
(04:58:07 PM) pearu: what do you mean? hashing is needed for fast dictionary lookups, finially strict comparison is needed anyway
(04:58:32 PM) ondrej: I thought you just compare the dictionaries
(04:58:46 PM) ondrej: like {..} == {..}
(04:59:01 PM) pearu: yes
(04:59:05 PM) ondrej: yeah, and the __cmp__ method gets executed
(04:59:08 PM) ondrej: and there you compare directly
(04:59:12 PM) ondrej: ok, that makes sense
(04:59:19 PM) ondrej: we used to compare the hashes in the oldcore
(05:00:14 PM) pearu: the basic property of a hash values is that the equal objects share the hash value but the reverse may not be true
(05:00:31 PM) ondrej: of course. that's ok for lookups
(05:01:07 PM) ondrej: it sucks, that sympy is so buggy now. when I tried to port Mul and Add, it completely broke down. I need to disentangle the assumptions, but leave it in there in some nice (maybe slow) form, because sympy uses them quite a lot as I discovered
(05:01:31 PM) pearu: yes, I know
(05:02:08 PM) ondrej: also there is the caching problem. it's related, so it needs to be fixed at once.
(05:02:27 PM) pearu: when I tried to fix sympy core issues I got also frustrated because of so many dependencies that need to be taken care when changing core a bit
(05:03:05 PM) ondrej: yeah, but you think that sympycore will be different, when you port all the modules?
(05:03:10 PM) pearu: in sympycore we decided not to use caching until things will be stable and covered with good unittests
(05:03:45 PM) pearu: probably not, but I don;t have plans to port the modules
(05:04:21 PM) ondrej: so what are your plans?
(05:05:24 PM) ondrej: in sympy it was your decision to use caching from the beginning - but I too didn't see the danger. but I think when I fix the assumptions, it should be possible to turn caching on and off easily.
(05:05:40 PM) pearu: may fundametnal plan is to have a stable core module with all necessary features needed for extensions
(05:05:51 PM) ondrej: right
(05:06:09 PM) ondrej: but without the extensions, it is not easy to see that it has all the necessary featurures
(05:06:27 PM) pearu: caching is not bad, just finding bugs from other parts will be difficult when caching is turned on
(05:06:52 PM) ondrej: with the newcore in sympy, I thought it has all the featurees, and you too imho. But it didn't, it was just hard to see it
(05:07:41 PM) pearu: well, I think with current sympy/sympycore we know moreorless what features will be important
(05:07:59 PM) ondrej: yeah, that's true
(05:09:16 PM) ondrej: sympy is getting more integrated in SAGE. my plan is to be able to easily switch maxima and sympy in SAGE. this will discover a hell lot of new bugs
(05:10:05 PM) ondrej: if we could make sympy let's say just 2 or 4 times slower than maxima, it'd be fine
(05:10:27 PM) pearu: I think that we cannot be sure that core covers all the important features until we have done all the implementations, for example, the problem of assumptions seemed to have an easy solution using is_.. attributes but as soon as more complicated assumptions will be needed, the used assumption model breaks down
(05:10:54 PM) ondrej: and more complicated assumptions will be needed
(05:11:11 PM) pearu: yes, I totally agree
(05:11:21 PM) ondrej: another thing - you seem to depend on python2.5 only - I think a lot of people still use python2.4
(05:11:56 PM) ondrej: I think just imports are better in python2.5 and "with"
(05:12:55 PM) pearu: yes, I think relative imports are important to ensure that the right modules are loaded
(05:12:58 PM) ondrej: the imports are not an issue. And the "with" - that could be used for assumptions, but imho the core and sympy could be made in python2.4 (users can use 2.5 and "with" in their own code)
(05:13:30 PM) ondrej: (I think the imports can be done robust in 2.4 too)
(05:14:53 PM) pearu: My thinking is that when sympycore will be stable, then it can be ported back to 2.4 when it will be an issue for many users, may be by this time everybody uses 2.5 anyway
(05:15:31 PM) pearu: also, I think that some of the new features in Python actually simplify writing sympy-kind of package
(05:15:45 PM) ondrej: yeah, that's true
(05:16:11 PM) ondrej: btw, are you taking part in the scipy sprint right now?
(05:16:21 PM) pearu: decorators and metaclasses have simplified many things, especially in function/operator support
(05:16:36 PM) ondrej: those are in 2.4 too, aren't they?
(05:16:39 PM) pearu: no, I cannot travel with my leg
(05:16:48 PM) ondrej: I mean over IRC
(05:17:25 PM) pearu: I am always logged in in sympy IRC, so, over IRC I'll be available
(05:20:18 PM) ondrej: yes. but I was talking about scipy sprint
(05:20:21 PM) ondrej: :)
(05:22:03 PM) pearu: ahh, ok :)
(05:22:52 PM) pearu: you know, I am new to IRC and my first attempts to log in scipy IRC failed
(05:23:14 PM) ondrej: I see.
(05:23:21 PM) ondrej: btw, did you read Suresh email on sympy list?
(05:23:32 PM) pearu: I am surpriced that even got sympy IRC working, still don't know if I have it correctly setup
(05:24:08 PM) pearu: yes
(05:24:20 PM) ondrej: I think we need to keep it simple, so that people can join in
(05:24:30 PM) pearu: agree
(05:24:55 PM) ondrej: that I don't understand it, that doesn't mean anything, I am not a genius. But other people should understand it.
(05:25:15 PM) pearu: but I think we are still searching a simple way to implement sympy
(05:25:25 PM) pearu: I think nobody wants to write a complex code
(05:25:33 PM) ondrej: yep
(05:25:39 PM) pearu: when starting, everything is simple antil the code crows
(05:25:47 PM) ondrej: the oldcore was definitely simpler. but slow.
(05:26:38 PM) pearu: I'd say there will be always payoffs, but sympycore is also simpler than sympy
(05:27:00 PM) pearu: I am currently working on implifying function support in sympycore
(05:28:19 PM) ondrej: that's why I think we should have just port nice things iterativelyk, instead of moving to the new core, because now it's very difficult to simplify it
(05:29:05 PM) pearu: iterative simplication is one approach, another very efficient simplification approach is refactoring
(05:29:57 PM) ondrej: yeah. ok, I'll try to do some work tonight.
(05:30:05 PM) pearu: in sympy many modules depend on each others internals, in sympycore I have tried to refactor different functionalities to separate modules
(05:31:00 PM) pearu: I have also found that documenting internals helps to simplify the code as then one sees what is important and what code is actually needed
(05:32:27 PM) ondrej: yeah. but it's still a lot of work to port it again to sympy
(05:34:49 PM) pearu: I don't see other ways, as you see yourself when trying to improve sympy with respect to assumptions and Add/Mul stuff, the task is not easy even within the same package
(05:35:59 PM) pearu: in sympycore I initially though that creating a new sympy.core package will be enough but now it is basically three packages: sympy.core, sympy.arithmetic, sympy.logic
(05:36:39 PM) pearu: the hope was that sympy could just grab sympycore sympy.core package and be done with upgrading
(05:37:00 PM) ondrej: I know.
(05:37:27 PM) pearu: but this can only work when both packages are properly refactored and core packages are stable in their interface
(05:38:01 PM) ondrej: Agree.
(05:38:37 PM) ondrej: but my strategy is to attract people to help us. it's just too much work for one or two people
(05:38:49 PM) ondrej: so it needs to do the job now.
(05:39:14 PM) fredrik3 [i=fredrik@gamma.kvi.sgsnet.se] entered the room.
(05:39:31 PM) pearu: I think for core part, few people that too many is better, in extending the sympy, more people are better
(05:39:43 PM) fredrik3 is now known as fredrik
(05:39:49 PM) pearu: that: read than
(05:40:50 PM) pearu: hi fredrik, do you want to see the whole discussion? I can copypaste it to email
(05:41:23 PM) fredrik: no, but thanks
(05:41:34 PM) pearu: ok
(05:42:37 PM) ondrej: let's put the discussion into the wiki?
(05:42:38 PM) fredrik: my 2c is just that IS is never going to be faster than isinstance in the best case, and therefore i don't see a benefit with it
(05:42:51 PM) ondrej: so that fredrik can read it. :)
(05:42:56 PM) ondrej: to answer his question. :)
(05:43:44 PM) fredrik: and if there's no speed advantage, it's better to use the standard python idiom
(05:44:29 PM) ondrej: we were discussing exactly this - pearu, could you please add it do the sympycore wiki at sympy? my irc client doesn't show me the whole history
(05:44:30 PM) pearu: ok, I'll run few tests and report back here in few minutes
(05:44:32 PM) kirr [n=kirr@89.163.1.112] entered the room.
(05:44:53 PM) ondrej: hi kirr. people always come after a discussion. :))
```