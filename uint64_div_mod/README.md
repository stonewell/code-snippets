# calculate div and mod result between 2 uint64_t values without directly using / and % operator
on 32bit platform, if do unsigned 64bit div/mod, compiler will automatically link to 2 functions in libc, aullrem, aulldiv to do the real caculation, because the div result may > max 32bit int.
these two functions divll and divll64 demos how to calculate when 64bit int div 32bit int and 64bit div 64bit int.
the divll version just another way to calculate, it is always fine to use divll64
