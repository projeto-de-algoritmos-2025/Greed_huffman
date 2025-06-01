import tkinter as tk
from tkinter import ttk, scrolledtext
import heapq
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import math

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
        
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritmo de Huffman - Visualização Interativa")
        self.root.geometry("1200x800")
        
        # Configuração das abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba de entrada
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="Entrada")
        
        # Aba da árvore
        self.tree_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tree_frame, text="Árvore de Huffman")
        
        # Aba de códigos
        self.codes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.codes_frame, text="Códigos e Compressão")
        
        self.create_input_widgets()
        self.create_tree_widgets()
        self.create_codes_widgets()
        
        # Variáveis para armazenar dados do algoritmo
        self.text = ""
        self.frequencies = {}
        self.nodes = []
        self.root_node = None
        self.codes = {}
        self.steps_tree = []
        self.current_step = 0
        
    def create_input_widgets(self):
        # Frame de entrada
        input_label = ttk.Label(self.input_frame, text="Digite um texto para codificar com o algoritmo de Huffman:", font=("Arial", 12))
        input_label.pack(pady=10)
        
        self.text_input = scrolledtext.ScrolledText(self.input_frame, height=5, width=50, font=("Arial", 12))
        self.text_input.pack(pady=10)
        
        self.process_button = ttk.Button(self.input_frame, text="Processar", command=self.process_text)
        self.process_button.pack(pady=10)
        
        # Frame para exibir a tabela de frequências
        self.freq_frame = ttk.LabelFrame(self.input_frame, text="Tabela de Frequências")
        self.freq_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.freq_text = scrolledtext.ScrolledText(self.freq_frame, height=10, width=30, font=("Courier", 12))
        self.freq_text.pack(pady=10, fill='both', expand=True)
        
        # Explicação
        explanation = (
            "O algoritmo de Huffman é um método de compressão que usa códigos de tamanho variável. "
            "Caracteres mais frequentes recebem códigos mais curtos, enquanto os menos frequentes "
            "recebem códigos mais longos. Este algoritmo constrói uma árvore binária onde os "
            "caracteres são as folhas, e o caminho da raiz até a folha determina o código binário."
        )
        
        explain_label = ttk.Label(self.input_frame, text=explanation, font=("Arial", 10), wraplength=700)
        explain_label.pack(pady=10)
        
    def create_tree_widgets(self):
        # Frame de controle
        control_frame = ttk.Frame(self.tree_frame)
        control_frame.pack(pady=10)
        
        self.prev_button = ttk.Button(control_frame, text="Anterior", command=self.show_prev_step)
        self.prev_button.grid(row=0, column=0, padx=5)
        
        self.step_label = ttk.Label(control_frame, text="Passo 0/0")
        self.step_label.grid(row=0, column=1, padx=20)
        
        self.next_button = ttk.Button(control_frame, text="Próximo", command=self.show_next_step)
        self.next_button.grid(row=0, column=2, padx=5)
        
        # Frame para exibir a descrição do passo
        self.step_description = scrolledtext.ScrolledText(self.tree_frame, height=4, width=80, font=("Arial", 10))
        self.step_description.pack(pady=10)
        
        # Frame para o gráfico
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.tree_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def create_codes_widgets(self):
        # Frame para exibir os códigos
        self.codes_frame_inner = ttk.Frame(self.codes_frame)
        self.codes_frame_inner.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tabela de códigos
        self.codes_text = scrolledtext.ScrolledText(self.codes_frame_inner, height=10, width=50, font=("Courier", 12))
        self.codes_text.pack(pady=10, side=tk.LEFT, fill='both', expand=True)
        
        # Estatísticas de compressão
        self.stats_frame = ttk.LabelFrame(self.codes_frame_inner, text="Estatísticas de Compressão")
        self.stats_frame.pack(pady=10, side=tk.RIGHT, fill='both', expand=True)
        
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, height=10, width=50, font=("Courier", 12))
        self.stats_text.pack(pady=10, fill='both', expand=True)
        
    def process_text(self):
        self.text = self.text_input.get("1.0", "end-1c")
        if not self.text:
            return
            
        # Reinicializar variáveis
        self.frequencies = Counter(self.text)
        self.nodes = []
        self.codes = {}
        self.steps_tree = []
        self.current_step = 0
        
        # Mostrar frequências
        self.show_frequencies()
        
        # Construir a árvore de Huffman
        self.build_huffman_tree()
        
        # Gerar códigos
        self.generate_codes(self.root_node, "")
        
        # Mostrar códigos e estatísticas
        self.show_codes_and_stats()
        
        # Mostrar primeiro passo da árvore
        self.show_current_step()
        
        # Mudar para a aba da árvore
        self.notebook.select(1)
        
    def show_frequencies(self):
        self.freq_text.delete("1.0", tk.END)
        self.freq_text.insert(tk.END, "Caracter | Frequência\n")
        self.freq_text.insert(tk.END, "-" * 24 + "\n")
        
        for char, freq in sorted(self.frequencies.items()):
            display_char = repr(char)[1:-1] if char in ['\n', '\t', ' '] else char
            self.freq_text.insert(tk.END, f"{display_char:8} | {freq:5}\n")
            
    def build_huffman_tree(self):
        # Criar nós para cada caracter
        for char, freq in self.frequencies.items():
            node = HuffmanNode(char, freq)
            heapq.heappush(self.nodes, node)
        
        # Adicionar passo inicial
        self.add_tree_step("Nós iniciais ordenados por frequência", list(self.nodes))
        
        # Construir a árvore
        while len(self.nodes) > 1:
            # Remover os dois nós de menor frequência
            left = heapq.heappop(self.nodes)
            right = heapq.heappop(self.nodes)
            
            # Criar um novo nó interno
            internal = HuffmanNode(None, left.freq + right.freq)
            internal.left = left
            internal.right = right
            
            # Adicionar o novo nó à heap
            heapq.heappush(self.nodes, internal)
            
            # Adicionar este passo
            description = f"Combinando '{left.char or 'Interno'}' ({left.freq}) e '{right.char or 'Interno'}' ({right.freq}) para criar nó interno com frequência {internal.freq}"
            self.add_tree_step(description, list(self.nodes), left, right, internal)
        
        if self.nodes:
            self.root_node = self.nodes[0]
            self.add_tree_step("Árvore de Huffman final", [], self.root_node)
    
    def add_tree_step(self, description, current_nodes, *special_nodes):
        self.steps_tree.append({
            "description": description,
            "nodes": current_nodes.copy() if current_nodes else [],
            "special_nodes": special_nodes
        })
        
    def show_current_step(self):
        if not self.steps_tree:
            return
            
        step = self.steps_tree[self.current_step]
        
        # Atualizar descrição
        self.step_description.delete("1.0", tk.END)
        self.step_description.insert(tk.END, step["description"])
        
        # Atualizar contador de passos
        self.step_label.config(text=f"Passo {self.current_step + 1}/{len(self.steps_tree)}")
        
        # Ativar/desativar botões
        self.prev_button.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_step < len(self.steps_tree) - 1 else tk.DISABLED)
        
        # Desenhar a árvore
        self.draw_tree(step)
        
    def draw_tree(self, step):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Criar grafo
        G = nx.DiGraph()
        
        # Desenhar árvore especial se houver
        if step["special_nodes"]:
            # Se tivermos a árvore completa (último passo)
            if len(step["special_nodes"]) == 1 and step["special_nodes"][0] == self.root_node:
                self.add_node_to_graph(G, self.root_node)
                # Usar layout hierárquico para a árvore completa
                pos = self.hierarchical_layout(G, self.root_node)
            else:
                # Para passos intermediários, adicionar os nós especiais
                for node in step["special_nodes"]:
                    self.add_node_to_graph(G, node)
                # Layout para os nós intermediários
                pos = nx.spring_layout(G)
        # Caso contrário, apenas mostrar os nós iniciais em linha
        else:
            for i, node in enumerate(step["nodes"]):
                node_id = f"Node_{i}"
                if node.char:
                    label = f"'{node.char}': {node.freq}"
                else:
                    label = f"Int: {node.freq}"
                G.add_node(node_id, label=label)
            
            # Organizar os nós iniciais em linha horizontal
            pos = {}
            num_nodes = len(step["nodes"])
            if num_nodes > 0:
                for i in range(num_nodes):
                    node_id = f"Node_{i}"
                    pos[node_id] = (i / (num_nodes - 1 or 1), 0.5)
        
        # Cores dos nós com base no tipo (folha ou interno)
        node_colors = []
        for node in G.nodes():
            # Verificar se é nó folha (tem caractere) ou nó interno
            if isinstance(node, str) and node.startswith("Node_"):
                # Nós da lista inicial são azuis
                node_colors.append('skyblue')
            else:
                # Para nós da árvore, verde para folhas e laranja para internos
                label = G.nodes[node].get('label', '')
                if "Int:" in label:
                    node_colors.append('orange')
                else:
                    node_colors.append('lightgreen')
        
        # Desenhar nós e arestas
        nx.draw(G, pos, ax=ax, with_labels=False, node_size=800, node_color=node_colors)
        
        # Adicionar rótulos
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
        
        # Adicionar rótulos nas arestas
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        ax.set_axis_off()
        self.canvas.draw()
    
    def hierarchical_layout(self, G, root_node, width=1., height=1.):
        """Cria um layout hierárquico personalizado para a árvore de Huffman"""
        def _get_tree_height(node):
            if node is None:
                return 0
            return 1 + max(_get_tree_height(node.left), _get_tree_height(node.right))
        
        def _get_positions(node, x, y, width, level_height, positions):
            if node is None:
                return
                
            node_id = id(node)
            positions[node_id] = (x, y)
            
            # Se for um nó folha, não tem filhos
            if node.left is None and node.right is None:
                return
                
            # Calcular posições dos filhos
            next_y = y - level_height
            
            # Posicionar o filho esquerdo
            if node.left:
                _get_positions(node.left, x - width/2, next_y, width/2, level_height, positions)
                
            # Posicionar o filho direito
            if node.right:
                _get_positions(node.right, x + width/2, next_y, width/2, level_height, positions)
        
        # Obter a altura da árvore
        tree_height = _get_tree_height(root_node)
        
        # Calcular a altura de cada nível
        level_height = height / max(1, tree_height - 1) if tree_height > 1 else 0.5
        
        # Calcular posições
        positions = {}
        _get_positions(root_node, 0.5, 0.9, width/2, level_height, positions)
        
        return positions
        
    def add_node_to_graph(self, G, node, parent=None, edge_label=None, node_id=None):
        if node is None:
            return
            
        if node_id is None:
            node_id = id(node)
            
        # Adicionar o nó ao grafo
        if node.char:
            char_display = repr(node.char)[1:-1] if node.char in ['\n', '\t', ' '] else node.char
            label = f"'{char_display}': {node.freq}"
        else:
            label = f"Int: {node.freq}"
        
        G.add_node(node_id, label=label)
        
        # Adicionar aresta se tiver pai
        if parent:
            G.add_edge(parent, node_id, label=edge_label)
            
        # Adicionar filhos recursivamente
        if node.left:
            self.add_node_to_graph(G, node.left, node_id, '0', id(node.left))
        if node.right:
            self.add_node_to_graph(G, node.right, node_id, '1', id(node.right))
    
    def show_prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_current_step()
            
    def show_next_step(self):
        if self.current_step < len(self.steps_tree) - 1:
            self.current_step += 1
            self.show_current_step()
    
    def generate_codes(self, node, code):
        if node is None:
            return
            
        # Se for um nó folha, armazenar o código
        if node.char is not None:
            self.codes[node.char] = code
            
        # Recursivamente percorrer a árvore
        self.generate_codes(node.left, code + "0")
        self.generate_codes(node.right, code + "1")
    
    def show_codes_and_stats(self):
        # Mostrar códigos
        self.codes_text.delete("1.0", tk.END)
        self.codes_text.insert(tk.END, "Caracter | Código Huffman\n")
        self.codes_text.insert(tk.END, "-" * 30 + "\n")
        
        for char, code in sorted(self.codes.items()):
            display_char = repr(char)[1:-1] if char in ['\n', '\t', ' '] else char
            self.codes_text.insert(tk.END, f"{display_char:8} | {code}\n")
        
        # Calcular estatísticas
        self.stats_text.delete("1.0", tk.END)
        
        # Tamanho original (ASCII - 8 bits por caracter)
        original_size = len(self.text) * 8
        
        # Tamanho comprimido
        compressed_size = sum(len(self.codes[char]) * freq for char, freq in self.frequencies.items())
        
        # Taxa de compressão
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        # Tamanho médio do código
        avg_code_length = compressed_size / len(self.text)
        
        self.stats_text.insert(tk.END, f"Número de caracteres: {len(self.text)}\n\n")
        self.stats_text.insert(tk.END, f"Tamanho original (bits): {original_size}\n")
        self.stats_text.insert(tk.END, f"Tamanho comprimido (bits): {compressed_size}\n\n")
        self.stats_text.insert(tk.END, f"Taxa de compressão: {compression_ratio:.2f}%\n")
        self.stats_text.insert(tk.END, f"Comprimento médio do código: {avg_code_length:.2f} bits\n")
        
        # Adicionar demonstração do texto comprimido
        if self.text:
            self.stats_text.insert(tk.END, "\nDemonstração da Compressão:\n")
            # Mostrar os primeiros 20 caracteres do texto original
            sample_text = self.text[:20]
            sample_bits = ""
            for char in sample_text:
                if char in self.codes:
                    sample_bits += self.codes[char]
            
            self.stats_text.insert(tk.END, f"Texto original (primeiros 20 caracteres):\n{sample_text}\n\n")
            self.stats_text.insert(tk.END, f"Representação em bits (Huffman):\n{sample_bits}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanGameApp(root)
    root.mainloop()
