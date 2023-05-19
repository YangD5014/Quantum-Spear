"""
上传至代码仓库时 请不要设为public
作者 YANGJIANFEI

以下代码主要实现了论文中Markowiz组合投资优化问题的经典QAOA算法复现
需要额外说明的是 我自制了一种数据对象 .spear对象 吴洋同学注意一下
简洁起见 略去注释 
"""



import numpy as np
from qiskit_aer import Aer
from qiskit.circuit import QuantumCircuit
from qiskit.tools.visualization import plot_histogram
from qiskit.algorithms.minimum_eigensolvers import QAOA
from qiskit.algorithms.optimizers import SPSA,COBYLA
from qiskit.utils import algorithm_globals
from qiskit.primitives import Sampler
from qiskit_optimization.algorithms import MinimumEigenOptimizer,OptimizationResultStatus,SolutionSample
from qiskit.utils import QuantumInstance
from qiskit.visualization import plot_histogram
from qiskit.circuit.library.n_local.qaoa_ansatz import QAOAAnsatz
from typing import List, Tuple
import pickle
from qiskit.quantum_info import SparsePauliOp,Pauli
from copy import deepcopy,copy
#quantum_instance = QuantumInstance(backend=Aer.get_backend("aer_simulator_statevector"))

class QuantumFinance(object):
    def __init__(self,theta_1:float=0.3,theta_2:float=0.4,theta_3:float=0.3,n:int=4,b:int=10,g:int=2,DataFile:str=None) -> None:
        #变量说明: 略
        #Datafile 必须放到./data文件夹下 且是以.spear为文件后缀
        self.theta_1=theta_1
        self.theta_2=theta_2
        self.theta_3=theta_3
        self.n = n #预选项目数
        self.b = b #总共的资产金融 默认10(万)元
        self.g = g
        self.Gf = 1/(2**(g-1))
        self.datafile = DataFile
        self.n_qubit = self.n*self.g
        self.load_data() #加载数据
        # self.model=QuadraticProgram(name=f'量子金融组合投资问题 N={self.n} g={self.g}') #初始化
        self.generate_hamiltonian() #根据论文中提到的方式生成Ising Hamiltonian
        self.generate_initial_state()
        print('初始化成功!')
        
    def load_data(self):
        if self.datafile is not None:
            with open(file=f'./data/{self.datafile}.spear',mode='rb') as f:
                self.data = pickle.load(file=f)
        else:
            with open(file=f'./data/Combination_1.spear',mode='rb') as f:
                self.data = pickle.load(file=f)
        if self.data['Number'] != self.n:
            raise ValueError('加载进的数据属性冲突!')
        print(f'加载数据成功\n data={self.data}')
        
                
    def generate_initial_state(self):
        qc= QuantumCircuit(self.n_qubit,name='Mix State')
        qc.h(range(self.n_qubit))
        self.initial_state = qc
        
        
    def generate_hamiltonian(self):
        [setattr(self,f'_x{i+1}',i+1) for i in range(self.n)]
        term1_list=[]
        term2_list=[]
        for i in range(self.n):
            term1_pauli = Pauli(data=QuantumFinance.Z_label(n=self.n_qubit,i=i+1,j=None))
            term1_h1 = self._h(i=i+1)
            term1_list.append(SparsePauliOp(data=term1_pauli,coeffs=term1_h1))
            for j in range(self.n):
                term2_pauli=Pauli(data=QuantumFinance.Z_label(n=self.n_qubit,i=i+1,j=j+1))
                term2_J = self._J(i=i+1,j=j+1)
                term2_list.append(SparsePauliOp(data=term2_pauli,coeffs=term2_J))
        term1 = sum(term1_list)
        term2 = sum(term2_list)
        self.hamiltonian = term1+term2
        
    
    @staticmethod
    def Z_label(n:int,i:int,j:int=None):
        string = 'I' * n
        if j is None:
            if i>n:
                raise ValueError('i can not larger than n!')
            # 将字符串中的特定位置替换为 'Z'
            string = string[:n-i] + 'Z' + string[n+1-i:]
        else:
            if j>n:
                raise ValueError('i can not larger than n!')
            string = string[:n-i] + 'Z' + string[n+1-i:]
            string = string[:n-j] + 'Z' + string[n+1-j:]
        return string
            
    def _J(self,i:int,j:int):
        tmp = self.theta_2*((self.b*self.Gf)**2) + self.theta_3*self.data['Risk_Matrix'][i-1][j-1]
        return 0.25*tmp
                
    def _h(self,i:int):
        tmp = -1*self.theta_1*self.data['Profit_rates'][i-1]-2*self.theta_2*self.b**2*self.Gf
        return 0.5*tmp + sum([self._J(i=i,j=k+1) for k in range(self.n)])
    
    
    def run(self,reps:int=2):
        qaoa = QAOA(sampler=Sampler(),optimizer=COBYLA(),reps=reps)
        #qaoa.ansatz = QAOAAnsatz(cost_operator=ex1.hamiltonian,initial_state=ex1.initial_state)
        self.result = qaoa.compute_minimum_eigenvalue(operator=self.hamiltonian)
        print(self.result.best_measurement)
        
    def explain_result(self):
        self.answer_dict={}
        if self.result is None:
            raise RuntimeError('先运行run 再调用此函数!')
        string = self.result.best_measurement['bitstring']
        result = [string[i:i+self.g] for i in range(0, len(string), self.g)]
        self.answer = f'本次咨询共涉及资产{self.n}个,\n预算为{self.b}万元,投资分片数:{self.g}\n'
        for index,i in enumerate(result):
            if i=='0'*self.g:
                self.answer+=f'第{index+1}个资产,不投资 \n'
                self.answer_dict[index+1]='0%'
            if i!='0'*self.g:
                self.answer+=f'第{index+1}个资产,投资{1/self.g*int(i[::-1],2)*100}%\n'
                self.answer_dict[index+1]=f'{1/self.g*int(i[::-1],2)*100}%'
        print(self.answer)
        
        