from libcpp.vector cimport vector

cdef extern from "Randoms.h" namespace "cqumo":
    cdef cppclass RandomVariable:
        double eval()
    
    cdef cppclass Randoms:
        Randoms()
        Randoms(unsigned seed)
        
        RandomVariable* createConstant(double value)
        RandomVariable* createExponential(double rate)
        RandomVariable* createUniform(double a, double b)
        RandomVariable* createNormal(double mean, double std)
        RandomVariable* createErlang(int shape, double param)

        RandomVariable *createMixture(
            const vector[RandomVariable*]& vars,
            const vector[double]& weights)

        RandomVariable* createHyperExp(
            const vector[double]& rates,
            const vector[double]& weights)
        