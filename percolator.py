import random
import time
import copy

import itertools
import sys
import traceback

import time
import signal
import errno

class TimeoutError(Exception):
    pass

class Timeout:
    def __init__(self, seconds=0.49, error_message="Timeout of {0} seconds hit"):
        self.seconds = seconds
        self.error_message = error_message.format(seconds)
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

# Removes the given vertex v from the graph, as well as the edges attached to it.
# Removes all isolated vertices from the graph as well.
def Percolate(graph, v):
    # Get attached edges to this vertex, remove them.
    for e in IncidentEdges(graph, v):
        graph.E.remove(e)
    # Remove this vertex.
    graph.V.remove(v)
    # Remove all isolated vertices.
    to_remove = {u for u in graph.V if len(IncidentEdges(graph,u)) == 0}
    graph.V.difference_update(to_remove)

def GetVertex(graph, i):
    for v in graph.V:
        if v.index == i:
            return v
    return None

def IncidentEdges(graph, v):
    return [e for e in graph.E if (e.a == v or e.b == v)]

def IncidentSameColorEdges(graph, v):
    return [e for e in graph.E if ((e.a == v and e.b.color == v.color) or (e.b == v and e.a.color == v.color))]

def IncidentDiffColorEdges(graph, v):
    return [e for e in graph.E if ((e.a == v and e.b.color != v.color) or (e.b == v and e.a.color != v.color))]

"""def MaxPlayerVertices(graph,player):
    my_moves = [v for v in graph.V if v.color == player]
    move_pairs=[]
    for v in graph.V:
        #print("in for loop")
        if v.color == player:
            #print("in if statement")
            new_graph = copy.deepcopy(graph)
            original_vertex = GetVertex(new_graph, v.index)
            Percolate(new_graph, original_vertex)
            move_pairs.append([v, len([v for v in new_graph.V if v.color == player])])
    move_pairs.sort(key = lambda x: -x[1])
    #print(move_pairs)
    return move_pairs[0][0]

def MinOpponentVertices(graph, player):
    my_moves = [v for v in graph.V if v.color == player]
    move_pairs=[]
    for v in graph.V:
        #print("in for loop")
        if v.color == player:
            #print("in if statement")
            new_graph = copy.deepcopy(graph)
            original_vertex = GetVertex(new_graph, v.index)
            Percolate(new_graph, original_vertex)
            move_pairs.append([v, len([v for v in new_graph.V if v.color != player])])
    move_pairs.sort(key = lambda x: x[1])
    #print(move_pairs)
    return move_pairs[0][0]"""

class PercolationPlayer:
    # `graph` is an instance of a Graph, `player` is an integer (0 or 1).
    # Should return a vertex `v` from graph.V where v.color == -1

    def ChooseVertexToColor(graph, player):
        #print('call')
        try:
            #print("tried")
            with Timeout():
                #print("timeout")
                chosen_vertex = PercolationPlayer.ChooseVertexToColor_helper(copy.deepcopy(graph), player)[0]
                #print('chosen vertex')
                return chosen_vertex
        # If user code does not return within appropriate timeout, select random action.
        except TimeoutError as e:
            #print('timeout')
            #print(e)
            #traceback.print_exc(file=sys.stdout)
            undecideds = [[v,len(IncidentEdges(graph, v))] for v in graph.V if v.color == -1]
            undecideds.sort(key = lambda x: -x[1])
            chosen_vertex = undecideds[0][0]
            #print('chosen vertex')
            return chosen_vertex
        # 1000 trials 0.868
        """undecideds = [[v,len(IncidentEdges(graph, v))] for v in graph.V if v.color == -1]
        undecideds.sort(key = lambda x: -x[1])
        return undecideds[0][0]"""
        #start = time.time()
        # 1000 trials with 5: 0.867-0.875
        # 1000 trials with 6: 0.8665-0.881
        """if len(graph.V) >= 7:
            undecideds = [[v,len(IncidentEdges(graph, v))] for v in graph.V if v.color == -1]
            undecideds.sort(key = lambda x: -x[1])
            #print(undecideds[0][0])
            return undecideds[0][0]
        #end = time.time()
        return PercolationPlayer.ChooseVertexToColor_helper(graph, player)[0]"""

    def ChooseVertexToColor_helper(graph, player):
        my_moves = [v for v in graph.V if v.color == -1]
        p_wins = []
        for v in my_moves:
            new_graph = copy.deepcopy(graph)
            original_vertex = GetVertex(new_graph, v.index)
            original_vertex.color = player
            # Then I really only had one option, since I must be second player
            if len(my_moves)==1:
                return (v, PercolationPlayer.ChooseVertexToColor_helper_2ndplayer(new_graph, 1))
            your_moves = [v for v in new_graph.V if v.color == -1]
            p_win = 0
            for u in your_moves:
                new_new_graph = copy.deepcopy(new_graph)
                original_vertex_new = GetVertex(new_new_graph, u.index)
                original_vertex_new.color = 1-player
                if len([v for v in new_new_graph.V if v.color == -1]) == 0:
                    p_win = p_win + PercolationPlayer.ChooseVertexToRemove_helper(new_new_graph, player)[1]
                else:
                    p_win = p_win + PercolationPlayer.ChooseVertexToColor_helper(new_new_graph, player)[1]
            p_win = p_win/len(your_moves)
            p_wins.append(p_win)
        max_p = 0
        max_p_index = 0
        for i in range(len(p_wins)):
            if p_wins[i]>=max_p:
                max_p = p_wins[i]
                max_p_index = i
        #print((my_moves[max_p_index], max_p))
        return (my_moves[max_p_index], max_p)

    # Helper method for ChooseVertexToColor_helper
    # Called to determine how good a colored graph is as a starting point, if we're second player (player 1)
    def ChooseVertexToColor_helper_2ndplayer(graph, player):
        your_moves = [v for v in graph.V if v.color==1-player]
        p = 0
        for v in your_moves:
            new_graph = copy.deepcopy(graph)
            original_vertex = GetVertex(new_graph,v.index)
            Percolate(new_graph, original_vertex)
            if new_graph == None:
                p+=0
            elif len([v for v in new_graph.V if v.color == player])==0:
                p+=0
            else:
                #print(new_graph)
                p += PercolationPlayer.ChooseVertexToRemove_helper(new_graph, player)[1]
        return p/len(your_moves)

    # `graph` is an instance of a Graph, `player` is an integer (0 or 1).
    # Should return a vertex `v` from graph.V where v.color == player
    """def ChooseVertexToRemove(graph, player):
        choices = [[v,len(IncidentEdges(graph,v))] for v in graph.V if v.color == player]
        choices.sort(key = lambda x: x[1])
        return choices[0][0]"""
    def ChooseVertexToRemove(graph, player):
        try:
            #print("tried")
            with Timeout():
                #print("timeout")
                chosen_vertex = PercolationPlayer.ChooseVertexToRemove_helper(copy.deepcopy(graph), player)[0]
                #print('chosen vertex')
                return chosen_vertex
        # If user code does not return within appropriate timeout, select random action.
        except TimeoutError as e:
            #print('timeout')
            #print(e)
            #traceback.print_exc(file=sys.stdout)
            offensive=1
            defensive=0
            choices = [[v,offensive * len(IncidentDiffColorEdges(graph, v)) - defensive * len(IncidentSameColorEdges(graph, v)) ] for v in graph.V if v.color == player]
            choices.sort(key = lambda x: -x[1])
            """
            choices = [[v,len(IncidentEdges(graph,v))] for v in graph.V if v.color == player]
            choices.sort(key = lambda x: x[1])
            """
            chosen_vertex = choices[0][0]
            #print('chosen vertex')
            return chosen_vertex

        """if len(graph.V)>=10:
            #print("Too hard!")
            offensive=1
            defensive=0
            choices = [[v,offensive * len(IncidentDiffColorEdges(graph, v)) - defensive * len(IncidentSameColorEdges(graph, v)) ] for v in graph.V if v.color == player]
            choices.sort(key = lambda x: -x[1])
            return choices[0][0]"""
            #return MaxPlayerVertices(graph,player)
            #return MinOpponentVertices(graph, player)
            #return random.choice([v for v in graph.V if v.color == player])
        #print(PercolationPlayer.ChooseVertexToRemove_helper(graph, player)[1])
        #print("Removing")
        #return PercolationPlayer.ChooseVertexToRemove_helper(graph, player)[0]

    # Recursive helper. Returns a tuple, composed of the vertex to be removed
    # followed by the probability that I win
    def ChooseVertexToRemove_helper(graph, player):
        my_moves = [v for v in graph.V if v.color == player]
        p_wins = []
        # Consider each of my possible moves
        for v in my_moves:
            new_graph = copy.deepcopy(graph)
            original_vertex = GetVertex(new_graph, v.index)
            Percolate(new_graph, original_vertex)
            # Check if the game is over (if and elif statements). If it is, I win
            if new_graph == None:
                return (v, 1)
            your_moves = [v for v in new_graph.V if v.color == ((player+1)%2)]
            if len(your_moves)==0:
                return (v, 1)
            # Probability that I win
            # Note that if p_win = 1, then it's a win for my player, so I win
            # Otherwise, it's technically a win for the other player, but he might mess up, so I might still be able to win
            p_win = 0
            # Consider each of the other player's moves in response
            for u in your_moves:
                new_new_graph = copy.deepcopy(new_graph)
                original_vertex_new = GetVertex(new_new_graph, u.index)
                Percolate(new_new_graph, original_vertex_new)
                if new_new_graph != None and len([v for v in new_new_graph.V if v.color == player]) > 0:
                    p_win += PercolationPlayer.ChooseVertexToRemove_helper(new_new_graph, player)[1]
            p_win = p_win/len(your_moves) # Average of the win probabilities for each move, since the other player chooses randomly
            p_wins.append(p_win)

        # Find the best move (highest win probability)
        max_p = 0
        max_p_index = 0
        for i in range(len(p_wins)):
            if p_wins[i]>=max_p:
                max_p = p_wins[i]
                max_p_index = i
        #print((my_moves[max_p_index], max_p))
        return (my_moves[max_p_index], max_p)

