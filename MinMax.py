import  numpy as np
import math 

def Heuristic(board):
    
    #l heuristica deve ritornare un max se sei un bianco
    #il max sarà la distanza in R2 del re dalla strada di casa
    #deve avere un peso positivo se il posizionamento d una pedina bianca mangia una nera
    
    #l'heurisica deve avere minimo se la pedina nera 
    #deve ritornare un max se mangia una pedina bianca
    #sommato a quanto distano due pedine nere scelte random da ogni lato a mangiare il Re
    
    return None


def minmax(position,depth,alpha=-np.inf,beta=+np.inf,maximizingPlayer=None):
    if depth==0 :
        return Heuristic(position)
    if maximizingPlayer=="White":
        maxEval=-np.inf
        for child in position.children():
            eval=minmax(child,depth-1,alpha,beta,"Black")
            maxEval=max(maxEval,eval)
            alpha=max(alpha,eval)
            if beta<=alpha:
                break
        return maxEval
    else:
        minEval=+np.inf
        for child in position.children():
            eval=minmax(child,depth-1,alpha,beta,"White")
            minEval=min(minEval,eval)
            beta=min(beta,eval)
            if beta<=alpha:
                break
        return minEval
    
                
                
        
        