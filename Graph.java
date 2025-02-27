//Hamzah Mughal 231400135 BFS and DFS
import java.util.*;

class Graph {
    private int vertices;
    private int[][] adjacencyMatrix;

    public Graph(int vertices) {
        this.vertices = vertices;
        adjacencyMatrix = new int[vertices][vertices];
    }

    public void addEdge(int src, int dest) {
        adjacencyMatrix[src][dest] = 1;
        adjacencyMatrix[dest][src] = 1; 
    }

    public void printAdjacencyMatrix() {
        System.out.println("Adjacency Matrix:");
        for (int i = 0; i < vertices; i++) {
            for (int j = 0; j < vertices; j++) {
                System.out.print(adjacencyMatrix[i][j] + " ");
            }
            System.out.println();
        }
    }

    public void dfs(int startNode) {
        Stack<Integer> stack = new Stack<>();
        boolean[] visited = new boolean[vertices];  
        stack.push(startNode);

        while (!stack.isEmpty()) {
            int currentNode = stack.pop();
            if (visited[currentNode]) {
                continue;
            }
            System.out.print(currentNode + " ");
            visited[currentNode] = true;

            for (int i = vertices - 1; i >= 0; i--) {
                if (adjacencyMatrix[currentNode][i] == 1 && !visited[i]) {
                    stack.push(i);
                }
            }
        }
        System.out.println();
    }

    public void bfs(int startNode) {
        Queue<Integer> queue = new LinkedList<>();
        boolean[] visited = new boolean[vertices];  
        queue.add(startNode);

        while (!queue.isEmpty()) {
            int currentNode = queue.poll();
            if (visited[currentNode]) {
                continue;
            }
            System.out.print(currentNode + " ");
            visited[currentNode] = true;

            for (int i = 0; i < vertices; i++) {
                if (adjacencyMatrix[currentNode][i] == 1 && !visited[i]) {
                    queue.add(i);
                }
            }
        }
        System.out.println();
    }

    public static void main(String[] args) {
        Graph graph = new Graph(5);
        graph.addEdge(0, 1);
        graph.addEdge(0, 2);
        graph.addEdge(1, 3);
        graph.addEdge(2, 4);
        graph.addEdge(3, 4);

        graph.printAdjacencyMatrix();
        
        System.out.println("DFS Traversal:");
        graph.dfs(0);
        
        System.out.println("BFS Traversal:");
        graph.bfs(0);
    }
}

// Practice task
//
// Using BFS
// 0, 3, 4, 5, 2, 7, 6
//
// Using DFS
// 0, 3, 4, 5, 2, 7




