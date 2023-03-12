#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 13:04:09 2023

@author: lau
"""

from multiprocessing import Process
from multiprocessing import Lock
from multiprocessing import Value, Array
from time import sleep
from random import random, randint

N = 100 #max
K = 5 #numero de elementos de cada proceso 
NPROD = 3 #numero de procesos

def delay(factor = 3):
    sleep(random()/factor)



def producir (storage, i, mutex):
    mutex.acquire()
    try:
        maximo=max(storage[i], 0)
        producto= randint(maximo, N)
        storage[i]=producto
        print ("El almacenamiento actual es:", storage[:])
        delay()
    finally:
        mutex.release()
        

def productor(storage, empty, non_empty, i, mutex):
    for v in range(K):
        delay()
        empty.acquire()
        producir(storage, i, mutex)
        non_empty.release()
        print (f"El productor {i} ha producido {storage[i]}")
    empty.acquire()
    mutex.acquire()
    try:
        storage[i] = -1
    finally:
        mutex.release()
        non_empty.release()
        
def consumir (storage, minimo, index, merge, indice, mutex):
    mutex.acquire()
    try:
        merge[index.value]= minimo
        storage[indice]=-2
    finally:
        mutex.release()
        
def consumidor(storage, index, merge, empty, non_empty, mutex):
    for v in non_empty:
        v.acquire()
    minimo=N+1
    i=0
    for m in storage:
        if m<minimo and m!=-1 and m!=-2:
            minimo=m
            indice=i
        if m<minimo and m==-2:
            minimo=N
            i=i+1
    
    while minimo!=N+1:
        consumir (storage, minimo, index, merge, indice, mutex)
        print (f"El consumidor ha consumido {minimo}")
    empty[indice].release() 
    non_empty[indice].acquire()

def main():
    storage = Array('i', NPROD)
    index = Value('i', 0)
    merge = Array('i', 500)
    for i in range(NPROD):
        storage[i] = -2
        
    print ("El almacen inicial es:", storage[:], "indice", index.value)

    non_empty = []
    empty = []
    mutex = Lock()
    for p in range(NPROD):
        non_empty.append(Lock())
        empty.append(Lock())
    for v in non_empty:
        v.acquire()

    prodlst = [ Process(target=productor,
                        name=f'prod_{i}',
                        args=(storage, empty[i], non_empty[i], i, mutex))
                for i in range(NPROD) ]
    consum= [ Process(target=consumidor,
                      name=f"cons_{i}",
                      args=(storage, index, merge, empty, non_empty, mutex))]

    for p in prodlst+consum: 
        p.start()

    for p in prodlst+consum:
        p.join()


if __name__ == '__main__':
    main()
