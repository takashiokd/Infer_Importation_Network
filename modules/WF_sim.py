import numpy as np
import random
from scipy.special import gamma, factorial
from scipy.stats import levy_stable
# def WF(A, NS, counts_deme,Nlins):
#     ### A is an operator acting on frequencies ###
    
#     ND,T = counts_deme.shape
    
#     n=3000 # total number of sublineages. (By combining these, construct Nlins superlineages )
#     B=np.zeros((T,n,ND))
#     #Initialize
#     for i in range(ND):
#         aux=np.ones(n)/n
#         B[0,:,i]=np.random.multinomial(NS[i], aux, size=1)/NS[i]
#     for t in range(1,T):
#         aux = B[t-1,:,:].T
#         aux = np.matmul(A,aux)
#         for i in range(ND):
#             B[t,:,i]=np.random.multinomial(NS[i], aux[i], size=1)/NS[i]   

#     Bnoise=np.zeros(B.shape)
#     for i in range(T):
#             for j in range(ND):
#                 Bnoise[i,:,j] =np.random.multinomial(counts_deme[j,i], B[i,:,j], size=1)/counts_deme[j,i]

#     aux=np.array(range(n))
#     random.shuffle(aux)
#     set_lins=np.array_split(aux ,Nlins)

#     B=np.zeros((T,Nlins,ND))#Observed superlineage frequencies
#     for i in range(Nlins):
#         B[:,i,:] = np.sum(Bnoise[:,set_lins[i],:],axis=1)
        
#     return B



# def WF_sim(Npop,counts_per_demeweek, ND, T, A=None):
    
#     if A is None:
#         if ND==2:
#             A=np.array([[0.6,0.4],[0.2,0.8]])
#         if ND==3:
#             A=np.array([[0.6,0.25,0.15],[0.2,0.8,0.0],[0.1,0.05,0.85]])

#         if ND>3:
#             A = np.zeros((ND,ND))
#             for i in range(ND):
#                 for j in range(ND):
#                     A[i,j]=np.random.pareto(1)
#                 A[i,i] += 3*np.sum(A[i])
#                 A[i]*=1.0/np.sum(A[i])
#     else:
#         A = A
#     NS=np.array([Npop]*ND) #Controls the strength of stochasticity (in transition probability)
#     counts_deme=np.ones((ND,T))*counts_per_demeweek #number of reported sequences in each deme/week

#     n=1000 # total number of sublineages. (By combining these, construct Nlins superlineages )
#     B=np.zeros((T,n,ND))
#     #Initialize
#     for i in range(ND):
#         #aux=np.random.dirichlet([1]*n, size = 1)[0]#np.ones(n)/n

#         aux=np.random.pareto(a=2, size=n)
#         aux = aux/np.sum(aux)
#         B[0,:,i]=np.random.multinomial(NS[i], aux, size=1)/NS[i]
#     for t in range(1,T):
#         aux = B[t-1,:,:].T
#         aux = np.matmul(A,aux)
#         for i in range(ND):
#             B[t,:,i]=np.random.multinomial(NS[i], aux[i], size=1)/NS[i]   

#     counts=np.zeros(B.shape)
#     for i in range(T):
#             for j in range(ND):
#                 counts[i,:,j]  =np.random.multinomial(counts_deme[j,i], B[i,:,j], size=1)
#     counts=counts.transpose([2,1,0])
    
#     return A,counts


###################

# Sum of Pareto variables

def ymin_one(alpha):
    #Determine the lower cutoff ymin such that E[y]=1, where y ~ ParetoI
    if alpha>1:
        res=(alpha-1)/alpha
    elif alpha==1:
        res=1 #The mean is ill-defined for alpha=1, but this is fine because the frequency dynamics is independent of the choice of ymin
    return res

def ParetoI(alpha,ymin, size):
    #ParetoI is genered from ParetoII generated by np.random.pareto
    return ymin*(1+np.random.pareto(alpha,size=size))
    

def stable_a(alpha,ymin,M):
    c = np.power(ymin,alpha)
    if alpha<1 and alpha>0:
        res=0
    elif alpha==1:
        res = c*M*np.log(M)
    elif alpha>1:
        res = M*ymin*alpha/(alpha-1)
 
    return res

def stable_b(alpha,ymin,M):
    
    c = np.power(ymin,alpha)
    
    if alpha<1 and alpha>0:
        res=np.power(np.pi*M*c/(2*gamma(alpha) *np.sin(np.pi*alpha/2)) ,1/alpha)
    elif alpha==1:
        res = np.pi*M*c/2
    elif alpha>1 and alpha<2:
        res = np.power(np.pi*M*c/(2*gamma(alpha) *np.sin(np.pi*alpha/2)) ,1/alpha)
    elif alpha==2:
        res = np.power(c*M*np.log(M),0.5)
    elif alpha>2:
        var = (ymin**2)*alpha/(((alpha-1)**2)*(alpha-2))
        res = np.power(M*0.5*var,0.5)
    
    return res
    
def rv_paretosum(alpha,ymin,M):
    #Compute the sum Y of M ParetoI variables y
    if M<1000:
        #When M is small 
        Y = np.sum(ParetoI(alpha,ymin, size=M))
    else:
        if alpha<2:
            rand=levy_stable.rvs(alpha, beta=1, loc=0, scale=1, size=1, random_state=None)[0]
        if alpha>=2:
            rand=levy_stable.rvs(2, beta=1, loc=0, scale=1, size=1, random_state=None)[0]
        Y = stable_a(alpha,ymin,M)+ rand*stable_b(alpha,ymin,M)   
    return Y

def WF_pareto_sim(alpha, Npop,counts_per_demeweek, ND, T, A=None,Nmicrolins=400, freqini=[]):
    
    if A is None:
        print('A is not provided! A_demo is used.')
        if ND==2:
            A=np.array([[0.6,0.4],[0.2,0.8]])
        if ND==3:
            A=np.array([[0.6,0.25,0.15],[0.2,0.8,0.0],[0.1,0.05,0.85]])

        if ND>3:
            A = np.zeros((ND,ND))
            for i in range(ND):
                for j in range(ND):
                    A[i,j]=np.random.pareto(1)
                A[i,i] += 2*np.sum(A[i])
                A[i]*=1.0/np.sum(A[i])
    else:
        A = A
    
    if type(Npop)==int:
        NS=np.array([Npop]*ND) #Controls the strength of stochasticity (in transition probability)
        n=np.min([400,Npop]) # total number of sublineages.
    else:# if the list of Npop is provided
        NS = Npop 
        n=np.min([Nmicrolins,np.min(Npop)])

    if type(counts_per_demeweek)==int:
        counts_deme=np.ones((ND,T))*counts_per_demeweek
    else:
        counts_deme=counts_per_demeweek
        

    
    B=np.zeros((T,n,ND))
    if freqini ==[]: 
        for i in range(ND):
            #aux=np.random.dirichlet([1]*n, size = 1)[0]#np.ones(n)/n
            aux=np.random.pareto(a=1.5, size=n)#Assume a power-law intitial distribution
            aux = aux/np.sum(aux)
            B[0,:,i]=np.random.multinomial(NS[i], aux, size=1)/NS[i]
    else:
        for i in range(ND):
            B[0,:,i]=freqini[i,:]
        
        # B[0,:,i]= np.array([1.0/n]*n)
        
    if alpha!=0:
        ymin=ymin_one(alpha)
    for t in range(1,T):
        aux = B[t-1,:,:].T
        aux = np.matmul(A,aux)
    
        for i in range(ND):
            if alpha!=0:# WF for alpha=0
                aux[i] = np.array([rv_paretosum(alpha,ymin,(int)(NS[i]*aux[i,k])) for k in range(n)])
                aux[i] *=1.0/np.sum(aux[i])
            B[t,:,i] =np.random.multinomial(NS[i],aux[i], size=1)/NS[i]
            
            #B[t,:,i] = np.array([freq_after_jackpot_pseudo(aux[i,k],lst_offsp,NS[i]) for k in range(n)])
            #B[t,:,i]=np.random.multinomial(NS[i], aux[i], size=1)/NS[i]   
    
    counts=np.zeros(B.shape)
    for i in range(T):
            for j in range(ND):
                counts[i,:,j]  =np.random.multinomial(counts_deme[j,i], B[i,:,j], size=1)
    counts=counts.transpose([2,1,0])
    
    return A,counts


# def freq_after_jackpot(p,a,M):
#     X =np.sum((a-1)*np.random.pareto(a, (int)(p*M)))
#     Y =np.sum((a-1)*np.random.pareto(a, (int)((1-p)*M)))
#     return X/(X+Y)

# def freq_after_jackpot_pseudo(p,lst_offsp,M):
#     X =np.sum( np.random.choice(lst_offsp,(int)(p*M) ))
#     Y =np.sum( np.random.choice(lst_offsp,(int)((1-p)*M) ))
#     return X/(X+Y)
# def WF_pareto_sim(a, Npop,counts_per_demeweek, ND, T, A=None):
    
#     lst_offsp= np.random.pareto(a, 10000000)
    
#     if A is None:
#         if ND==2:
#             A=np.array([[0.6,0.4],[0.2,0.8]])
#         if ND==3:
#             A=np.array([[0.6,0.3,0.1],[0.2,0.8,0.0],[0.1,0.1,0.8]])

#         if ND>3:
#             A = np.zeros((ND,ND))
#             for i in range(ND):
#                 for j in range(ND):
#                     A[i,j]=np.random.pareto(1)
#                 A[i,i] += 3*np.sum(A[i])
#                 A[i]*=1.0/np.sum(A[i])
#     else:
#         A = A
#     NS=np.array([Npop]*ND) #Controls the strength of stochasticity (in transition probability)
#     counts_deme=np.ones((ND,T))*counts_per_demeweek #number of reported sequences in each deme/week

#     n=2000 # total number of sublineages. (By combining these, construct Nlins superlineages )
#     B=np.zeros((T,n,ND))
#     #Initialize
#     for i in range(ND):
#         #aux=np.random.dirichlet([1]*n, size = 1)[0]#np.ones(n)/n

#         aux=np.random.pareto(a=2, size=n)
#         aux = aux/np.sum(aux)
#         B[0,:,i]=np.random.multinomial(NS[i], aux, size=1)/NS[i]
#     for t in range(1,T):
#         aux = B[t-1,:,:].T
#         aux = np.matmul(A,aux)
    
#         for i in range(ND):
#             #B[t,:,i] = np.array([freq_after_jackpot(aux[i,k],a,NS[i]) for k in range(n)])
#             B[t,:,i] = np.array([freq_after_jackpot_pseudo(aux[i,k],lst_offsp,NS[i]) for k in range(n)])
#             B[t,:,i] *=1.0/np.sum(B[t,:,i])
#             #B[t,:,i]=np.random.multinomial(NS[i], aux[i], size=1)/NS[i]   
    
#     counts=np.zeros(B.shape)
#     for i in range(T):
#             for j in range(ND):
#                 counts[i,:,j]  =np.random.multinomial(counts_deme[j,i], B[i,:,j], size=1)
#     counts=counts.transpose([2,1,0])
    
#     return A,counts


def WF_sim(Npop,counts_per_demeweek, Csn, ND, T, A=None,Ntraj=100, freqini=[]):
    
    if A is None:
        print('A is not provide! A_demo is used.')
        if ND==2:
            A=np.array([[0.6,0.4],[0.2,0.8]])
        if ND==3:
            A=np.array([[0.6,0.25,0.15],[0.2,0.8,0.0],[0.1,0.05,0.85]])

        if ND>3:
            A = np.zeros((ND,ND))
            for i in range(ND):
                for j in range(ND):
                    A[i,j]=np.random.pareto(1)
                A[i,i] += 2*np.sum(A[i])
                A[i]*=1.0/np.sum(A[i])
    else:
        A = A
    
    if type(Npop)==int:
        NS=np.array([Npop]*ND) #Controls the strength of stochasticity (in transition probability)
    else:# if the list of Npop is provided
        NS = Npop 
    
    B=np.zeros((T,Ntraj,ND))
    
    if freqini ==[]: 
        for i in range(ND):
            aux=np.random.pareto(a=10, size=Ntraj)#Assume a power-law intitial distribution
            aux = aux/np.sum(aux)
            B[0,:,i]=np.random.multinomial(NS[i], aux, size=1)/NS[i]
    else:
        for i in range(ND):
            B[0,:,i]=freqini[i,:]
        
    for t in range(1,T):
        aux = B[t-1,:,:].T
        aux = np.matmul(A,aux)
        for l in range(Ntraj): 
            for i in range(ND):
                B[t,l,i] =np.random.binomial(NS[i],aux[i,l], size=1)/NS[i]
 
    # Add sampling error
    if type(counts_per_demeweek)==int:
        counts_deme=np.ones((ND,T))*counts_per_demeweek
    else:
        counts_deme=counts_per_demeweek
    counts=np.zeros(B.shape)
    for t in range(T):
            for j in range(ND):
                for l in range(Ntraj):
                    counts[t,l,j]  =np.round(np.random.binomial(int(counts_deme[j,t]/Csn[j]), B[t,l,j], size=1)*Csn[j])
    counts=counts.transpose([2,1,0])

    return A,counts,B



def demo_WF_sim(Npop,counts_per_demeweek, Csn, ND, T, A=None,Ntraj=100, freqini=[]):
    
    if A is None:
        print('A is not provide! A_demo is used.')
        
        if ND==1:
            A=np.array([[1.0]])
        if ND==2:
            A=np.array([[0.6,0.4],[0.2,0.8]])
        if ND==3:
            A=np.array([[0.6,0.25,0.15],[0.2,0.8,0.0],[0.1,0.05,0.85]])

        if ND>3:
            A = np.zeros((ND,ND))
            for i in range(ND):
                for j in range(ND):
                    A[i,j]=np.random.pareto(1)
                A[i,i] += 2*np.sum(A[i])
                A[i]*=1.0/np.sum(A[i])
    else:
        A = A
        
    
    if type(Npop)==int:
        NS=np.array([Npop]*ND) #Controls the strength of stochasticity (in transition probability)
    else:# if the list of Npop is provided
        NS = Npop 
    

    if type(counts_per_demeweek)==int:
        counts_deme=np.ones((ND,T))*counts_per_demeweek
    else:
        counts_deme=counts_per_demeweek
        
    B=np.zeros((T,Ntraj,ND))
    B_obs=np.zeros((T,Ntraj,ND))
    
    if freqini ==[]: 
        for i in range(ND):
            aux=np.random.pareto(a=1.5, size=Ntraj)+1#Assume a power-law intitial distribution
            aux = aux/np.sum(aux)
            B[0,:,i]=np.random.multinomial(NS[i], aux, size=1)/NS[i]
    else:
        for i in range(ND):
            B[0,:,i]=freqini[i,:]
      
    for l in range(Ntraj):
        for t in range(1,T):
            for i in range(ND):
                for j in range(ND):
                    B[t,l,i] +=  A[i,j]*B[t-1,l,j]
                B[t,l,i] +=  np.sqrt(B[t-1,l,i]*(1-B[t-1,l,i])/NS[i])*np.random.normal()
                if B[t,l,i]<0:
                    B[t,l,i]=0
                elif B[t,l,i]>1:
                    B[t,l,i]=1
                
    # Add sampling error
    for l in range(Ntraj):
        for t in range(T):
            for i in range(ND):
                B_obs[t,l,i] = B[t,l,i] + np.sqrt(B[t,l,i]*(1-B[t,l,i])*Csn[i]/counts_per_demeweek[i,t])*np.random.normal()

                if B_obs[t,l,i]<0:
                    B_obs[t,l,i]=0
                elif B_obs[t,l,i]>1:
                    B_obs[t,l,i]=1      
    
    counts=np.zeros(B.shape)
    for t in range(T):
            for j in range(ND):
                for l in range(Ntraj):
                    counts[t,l,j]  = int( B_obs[t,l,j]*counts_per_demeweek[j,t] )
    counts=counts.transpose([2,1,0])

    return A,counts,B