#!/usr/bin/env python

##  PrimeGenerator.py
##  Author: Avi Kak
##  Date: February 18, 2011

import random

class PrimeGenerator( object ):   

    def __init__( self, **kwargs ):
        # type: (object) -> object
        # type: (object) -> object
        """

        :rtype: object
        """
        if 'bits' in kwargs: bits = kwargs.pop('bits')
        if 'debug' in kwargs: debug = kwargs.pop('debug')
        if 'emod' in kwargs: emod = kwargs.pop('emod')
        self.bits = bits
        self.debug = debug
        self.emod = emod

    def set_initial_candidate(self):
        candidate = random.getrandbits( self.bits )
        if candidate & 1 == 0: candidate += 1
        candidate |= (1 << self.bits-1)
        candidate |= (2 << self.bits-3)
        self.candidate = candidate
      
    def set_probes(self):
        self.probes = [2,3,5,7,11,13,17]

    # This is the same primality testing function as shown earlier
    # in Section 11.5.6 of Lecture 11:
    def test_candidate_for_prime(self):
        'returns the probability if candidate is prime with high probability'
        if any([self.candidate % a == 0 for a in self.probes]): return 0
        p = self.candidate
        # need to represent p-1 as  q * 2^k  
        k, q = 0, self.candidate-1
        while not q&1:  # while q is even
            q >>= 1
            k += 1
        if self.debug: print("q = ", q, " k = ", k)
        for a in self.probes:
            a_raised_to_q = pow(a, q, p)     
            if a_raised_to_q == 1 or a_raised_to_q == p-1: continue
            a_raised_to_jq = a_raised_to_q
            primeflag = 0
            for j in range(k-1):
                a_raised_to_jq = pow(a_raised_to_jq, 2, p) 
                if a_raised_to_jq == p-1: 
                    primeflag = 1
                    break
            if not primeflag: return 0
        self.probability_of_prime = 1 - 1.0/(4 ** len(self.probes))
        return self.probability_of_prime

    def findPrime(self):
        self.set_initial_candidate()
        if self.debug:  print("        candidate is: ", self.candidate)
        self.set_probes()
        if self.debug:  print("        The probes are: ", self.probes)
        while 1:
            if self.test_candidate_for_prime():
                if self.debug:
                    print("Prime number: ", self.candidate, \
                       " with probability: ", self.probability_of_prime)
                break
            else:
                self.candidate += 2
                while self.candidate % self.emod == 1:
                    self.candidate += 2
                if self.debug: print("        candidate is: ", self.candidate)
        return self.candidate

if __name__ == '__main__':
    
    generator = PrimeGenerator( bits = 128, debug = 0, emod = 65537)
    prime = generator.findPrime()

    print("Prime returned: ", prime)