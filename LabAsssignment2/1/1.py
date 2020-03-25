import numpy as np

def main():
    #A
    M = np.arange(2,27)
    print(M)
    #B
    M = M.reshape(5,5)
    print(M)
    #C
    for i in range(1,4):
        for j in range(1,4):
            M[i][j] = 0;
    print(M)
    #D
    M = M @ M
    print(M)
    #E
    v = M[:1,:]
    v = v * v;
    temp = 0.0
    for i in range(5):
        temp += v[0][i]
    print(np.sqrt(temp))
    
if __name__ == "__main__":
    main()
            
    