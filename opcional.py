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


def producir (storage, i, cola, numero, mutex):
    mutex.acquire()
    try:
        maximo=max(numero, 0)
        producto= randint(maximo, N)
        cola.put(producto)
        print (f"El productor {i} ha producido {producto}")
        delay()
    finally:
        mutex.release()
    return producto
        

def productor(storage, empty, non_empty, i, cola, mutex):
    numero=0
    for v in range(K):
        delay()
        empty.acquire()
        producto=producir(storage, i, cola, numero, mutex)
        numero=producto
        non_empty.release()
    
    
    
      
def consumir(storage, minimo, index, merge, indice, cola, mutex):
    mutex.acquire()
    try:
        merge[index.value]= minimo
        delay()
        index.value = index.value + 1  
        
        
    finally:
        mutex.release()
        

            
def consumidor(storage, index, merge, empty, non_empty, cola, mutex):
    for v in non_empty:
        v.acquire()
    producido=[]
    for k in range(len(storage)):
        producido.append(0)
        if storage[k]==-2:
            storage[k]=cola[k].get()
    
    
    minimo=0
    while minimo!=N+1:
        minimo=N+1
        
        for k in range(len(storage)):
            if storage[k]<minimo and storage[k]>=0:
                minimo=storage[k]
                indice=k
        
               
        if minimo!=N+1:
            print (f"El consumidor ha consumido {minimo}")
            non_empty[indice].acquire()
            print(f"{producido[indice]}, {indice}")
            producido[indice] +=1
            if producido[indice] == (K-1):
                storage[indice]=-1
                
            else:
                elemento=cola[indice].get()
                storage[indice]=elemento
                empty[indice].release()
                
            print ("El almacenamiento actual es:", storage[:]) 
            
            consumir(storage, minimo, index, merge, indice, cola, mutex)
            
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
                      args=(storage, index, merge, empty, non_empty, cola, mutex))]

    for p in prodlst+consum: 
        p.start()
        
    

    for p in prodlst+consum:
        p.join()
        
    print("El almacen final es:", merge[:])


if __name__ == '__main__':
    main()
