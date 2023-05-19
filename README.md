# Quantum-Spear
Quantum Spear 小组协作代码共享空间  
version == 1.0  
请前端同学阅读一下教程[点击这里](https://github.com/YangD5014/Quantum-Spear/blob/main/tutorial_yang.ipynb)  
本次的例子背景  
拥有的总资产是B,其中有n个理财产品可以选择,  
每个理财产品的收益率是 $m_i$, 风险的协方差矩阵是 $p_{ij}$
| 资产 | 预期收益率 | 
| :----:| :----: | 
| 股票A | 8%| 
| 债券B | 5% | 
| 期货C | 10% | 
| REIT D | 6% |  

协方差矩阵 $p_{ij}$:  
| 资产 | 股票A | 债券B | 期货C | REIT D |
| --- | --- | --- | --- | --- |
| 股票A | 0.04 | 0.01 | 0.06 | 0.025 |
| 债券B | 0.01 | 0.02 | 0.03 | 0.005 |
| 商品C | 0.06 | 0.03 | 0.09 | 0.04 |
| REIT D | 0.025 | 0.005 | 0.04 | 0.09 |  

目标函数= $\max\sum_{i=1}^{n} \theta_1m_ix_i - \theta_2 \rho_{ij}x_ix_j-\theta_3(G_fbx_i-b)^2$  
其中 $\theta_1$代表着投资者对于利润的权重  
 $\theta_2$代表着投资者对于风险的权重  
 $x_i$代表着不同的理财产品  
例如风险敏感型消费者: $\theta_1 = 0.3$ $\theta_2 =0.4$  $\theta_3 = 0.3$  

<font color=yellow>重写目标函数: </font>  
  $\max\sum_{i=1}^{n} (\theta_1m_i+2\theta_3G_fb^2x_i)x_i - \theta_2 \rho_{ij}x_ix_j-\theta_3b^2G_f^2x_i^2-\theta_3b^2$ 
