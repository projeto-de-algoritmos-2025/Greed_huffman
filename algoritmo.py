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
        