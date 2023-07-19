import numpy as np
import matplotlib.pyplot as plt
from heapq import heappush, heappop

# Create a 10x10 map called "a" with random costs initialized
values = np.random.choice(np.arange(1, 101, 1), size=100, replace=False)
a = values.reshape((10, 10))
a[0][0] = 0
print(a)

# initialize start node , open and closed list and put start node in open list
# open list contains node which are discovered and not evaluated
# close list contains node which are discovered and evaluated and path is x and y co ordinates of all nodes from start to goal
start_node = (0, 0)
goal_node = (9, 9)
open_list = []
closed_list = []
path = [start_node]
came_from = {}
current_node = start_node

# Calculate the Euclidean distance between two points for h 
def eu_dist(a1, b1):
    d1 = (a1[0] - b1[0]) ** 2
    d2 = (a1[1] - b1[1]) ** 2
    d = d1 + d2
    distance = np.sqrt(d)
    return distance

# Calculate the g-score (path cost from start to current node)
def g_score(u):
    arr = []
    for ar in path:
        arr.append(a[ar[0]][ar[1]])
    g = sum(arr) + a[u[0]][u[1]]
    node = (u[0], u[1])
    return (g, node)

# Calculate the h-score (heuristic value) using Euclidean distance
def h_score(node):
    return eu_dist(goal_node, node)

# Calculate the f-score (sum of g and h-score)
def f_score(node):
    g = g_score(node)[0]
    h = h_score(node)
    return g + h

# Get the neighbors of a current node
def get_neighbors(x, y):
    neighbors = []

    # Check top neighbor
    if y > 0:
        top = (x, y - 1)
        neighbors.append(top)

    # Check bottom neighbor
    if y < len(a) - 1:
        bottom = (x, y + 1)
        neighbors.append(bottom)

    # Check left neighbor
    if x > 0:
        left = (x - 1, y)
        neighbors.append(left)

    # Check right neighbor
    if x < len(a) - 1:
        right = (x + 1, y)
        neighbors.append(right)

    # Check top-left neighbor
    if x > 0 and y > 0:
        top_left = (x - 1, y - 1)
        neighbors.append(top_left)

    # Check top-right neighbor
    if x < len(a) - 1 and y > 0:
        top_right = (x + 1, y - 1)
        neighbors.append(top_right)

    # Check bottom-left neighbor
    if x > 0 and y < len(a) - 1:
        bottom_left = (x - 1, y + 1)
        neighbors.append(bottom_left)

    # Check bottom-right neighbor
    if x < len(a) - 1 and y < len(a) - 1:
        bottom_right = (x + 1, y + 1)
        neighbors.append(bottom_right)

    return neighbors

# Add the start node to the open list and while open list is there, add current node to close list and remove current node from open list
heappush(open_list, (f_score(start_node), start_node))

while open_list:
    current_node = heappop(open_list)[1]
    closed_list.append(current_node)
    g = g_score(current_node)[0]
    h = h_score(current_node)
    f = g + h

# if current node is goal then break
    if current_node == goal_node:
        break
# get the neighbour of current node and find its minimum f score  
    neighbors = get_neighbors(current_node[0], current_node[1])

    for n in neighbors:
        if n in closed_list:
            continue

        t_g = g_score(n)[0]
        t_h = h_score(n)
        t_f = t_g + t_h
# if neighbour not in open list then add it, if niebour node g value is greater than current g value then skip the iteration
        if n not in [node[1] for node in open_list]:
            heappush(open_list, (t_f, n))
        elif t_f >= f:
            continue
        came_from[n] = current_node

# Reconstruct the path from the goal to the start
path = []
current = goal_node
while current != start_node:
    path.append(current)
    current = came_from[current]
path.append(start_node)
path.reverse()

print("our path is:", path)

def cost(list):
    cost_arr = []
    for l in list:
        cost = a[l[0]][l[1]]
        cost_arr.append(cost)
    print(sum(cost_arr))
    return cost


cost(path)
# print(cost(path))

x_coords = []
y_coords = []
for i in (range(0,len(path))):
    x = path[i][0]
    y = path[i][1]

    x_coords.append(x)
    y_coords.append(y)

# plot map and path

fig, ax = plt.subplots(figsize=(20,20))
ax.imshow(a, cmap=plt.cm.Blues,vmin = a.min(),vmax = a.max())
ax.scatter(start_node[1],start_node[0], marker = "*", color = "yellow", s = 200)
ax.scatter(goal_node[1],goal_node[0], marker = "*", color = "red", s = 200)
ax.plot(y_coords,x_coords, color = "black")
plt.show()

