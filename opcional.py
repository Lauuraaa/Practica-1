#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: lau
"""

from multiprocessing import Process, Queue
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import Value, Array
from time import sleep
from random import random, randint

N = 100 #max
K = 5 #numero de elementos de cada proceso 
NPROD = 3#numero de procesos

def delay(factor = 3):
    sleep(random()/factor)



def producir (storage, i, cola, mutex):
    mutex.acquire()
    try:
        maximo=max(storage[i], 0)
        producto= randint(maximo, N)
        cola.put(producto)
        storage[i]=producto
        print (f"El productor {i} ha producido {storage[i]}")
        print ("El almacenamiento actual es:", storage[:])
        delay()
    finally:
        mutex.release()
        

def productor(storage, empty, non_empty, i, cola, mutex):
    for v in range(K):
        delay()
        empty.acquire()
        producir(storage, i, cola, mutex)
        non_empty.release()
    cola.put(None)
    mutex.acquire()
    try:    
        storage[i] = -1
    finally:
        non_empty.release()
        mutex.release()
    
        
def consumir(storage, minimo, index, merge, indice, mutex):
    mutex.acquire()
    try:
        merge[index.value]= minimo
        delay()
        index.value = index.value + 1     
    finally:
        mutex.release()
        

        
def consumidor(storage, index, merge, empty, non_empty,  mutex):
    for v in non_empty:
        v.acquire()
    minimo=0
    while minimo!=N+1:
        minimo=N+1
        for k in range(len(storage)):
            if storage[k]<minimo and storage[k]>=0:
                minimo=storage[k]
                indice=k
        if minimo!=N+1:
            print (f"El consumidor ha consumido {minimo}")
            empty[indice].release()
            consumir(storage, minimo, index, merge, indice, mutex)
            non_empty[indice].acquire()
            delay()

def main():
    storage = Array('i', NPROD)
    index = Value('i', 0)
    merge = Array('i', 500)
    cola = []
    for i in range(NPROD):
        storage[i] = -2
        
    print ("El almacen inicial es:", storage[:], "indice", index.value)

    non_empty = []
    empty = []
    mutex = Lock()
    for p in range(NPROD):
        non_empty.append(Semaphore(0))
        empty.append(BoundedSemaphore(NPROD))
        cola.append(Queue())

    prodlst = [ Process(target=productor,
                        name=f'prod_{i}',
                        args=(storage, empty[i], non_empty[i], i, cola[i], mutex))
                for i in range(NPROD) ]
    consum= [ Process(target=consumidor,
                      name=f"cons_{i}",
                      args=(storage, index, merge, empty, non_empty, mutex))]

    for p in prodlst+consum: 
        p.start()
        
    

    for p in prodlst+consum:
        p.join()
        
    print("El almacen final es:", merge[:])


if __name__ == '__main__':
    main()
