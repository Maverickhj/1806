# MIT 18.06 线性代数快速学习路线

> 适用人群：职场人士，希望快速建立线性代数知识骨架；已经学习过 3Blue1Brown 的 *Essence of Linear Algebra*；偏向直接阅读材料，不看视频；NumPy 和 PyTorch 都不熟悉。
>
> 核心目标：**不是“完整学完一门本科课程”，而是快速建立可用于 AI / AI-Infra / 数值计算的 Linear Algebra Backbone。**

---

## 1. 总体学习策略

建议把 MIT 18.06 压缩成三层：

```text
第一层：理解数学结构
    ↓
第二层：用 NumPy 做极小实验
    ↓
第三层：未来迁移到 PyTorch / AI Infra
```

当前阶段只使用 **NumPy**。

原因：

- NumPy API 更简单，更接近教材中的矩阵与向量；
- 避免同时学习 `Tensor / autograd / device / dtype` 等 PyTorch 工程概念；
- 当前目标不是“学会 NumPy”，而是把 NumPy 当作一个可编程线性代数计算器。

推荐比例：

```text
阅读材料       60%
手算           20%
NumPy 实验     20%
```

不要追求刷大量题，也不要追求完整阅读教材。

---

# 2. 知识主线

第一遍只抓下面六个核心 Topic：

```text
1. Ax = b
   ↓
2. Rank + Four Fundamental Subspaces
   ↓
3. Orthogonality + Projection
   ↓
4. Least Squares + QR
   ↓
5. Eigenvalues + Symmetric / Positive Definite
   ↓
6. SVD
```

这六块基本构成之后理解以下问题的数学底座：

```text
Low-Rank Approximation
LoRA
PCA
Embedding
Linear Layer
Covariance
Hessian
Condition Number
Numerical Stability
Matrix Factorization
Quantization
Training Stability
```

---

# 3. 材料优先级

## 第一优先级：MIT 18.06 Lecture Summary

用途：

- 当成 syllabus；
- 确认一个 Topic 里有哪些关键概念；
- 不理解时再去教材查。

不要顺序精读所有材料。

建议阅读方式：

```text
Lecture Summary
      ↓
发现不懂的定义 / 推导
      ↓
查 Strang 教材对应章节
      ↓
做 1~2 个小题 / NumPy 实验
      ↓
进入下一个 Topic
```

---

## 第二优先级：Gilbert Strang《Introduction to Linear Algebra》

把教材当作：

> 随机访问知识库

而不是：

> 从第一页读到最后一页的小说。

重点读：

- 定义
- 核心定理
- 关键推导
- 例题
- 图示

暂时跳过大量重复练习。

---

## 第三优先级：MIT Problem Sets / Exams

使用方法：

```text
学完 Topic
   ↓
随机做 2~3 题
   ↓
能做
   → 下一章

不会
   → 回材料补概念
   → 再做 1 题
```

第一遍不需要完整刷所有 Problem Set。

---

# 4. 7 天 Material-Only Sprint

每天建议投入：

```text
60 ~ 90 分钟
```

如果时间充裕，可以一天推进两个 Topic。

---

## Day 0：NumPy 最小准备

目标不是系统学习 NumPy，只学线性代数需要的最小集合。

### 必须掌握

```python
import numpy as np

A = np.array(...)
A.shape
A.T

A @ B
A @ x

np.eye(...)
np.zeros(...)
np.ones(...)
```

以及：

```python
np.linalg.solve(A, b)
np.linalg.matrix_rank(A)
np.linalg.lstsq(A, b, rcond=None)
np.linalg.qr(A)
np.linalg.eig(A)
np.linalg.eigh(A)
np.linalg.svd(A)
np.linalg.cond(A)
```

### Day 0 验收

能够读懂：

```python
A = np.array([
    [1., 2.],
    [3., 4.]
])

x = np.array([1., 1.])

y = A @ x
```

并知道：

```text
A.shape
A.T
A @ x
```

分别是什么意思即可。

---

# 5. Day 1：Ax = b、Elimination、LU

## 核心问题

先建立：

\[
Ax=b
\]

的三种理解：

### 1. 方程组视角

矩阵代表一个线性方程组。

### 2. Column Combination

如果：

\[
A=[a_1,a_2,\dots,a_n]
\]

那么：

\[
Ax=x_1a_1+x_2a_2+\dots+x_na_n
\]

所以：

\[
Ax=b
\]

本质是在问：

> b 能不能由 A 的列向量线性组合得到？

### 3. Linear Transformation

\[
A:\mathbb{R}^n \rightarrow \mathbb{R}^m
\]

---

## 必学

- Gaussian Elimination
- Pivot
- Invertible Matrix
- LU Factorization
- Singular Matrix

---

## 暂时不深挖

- Cramer's Rule
- Cofactor expansion
- 复杂 inverse 手算

---

## NumPy 实验

```python
import numpy as np

A = np.array([
    [2., 1.],
    [1., 3.]
])

b = np.array([1., 2.])

x = np.linalg.solve(A, b)

print(x)
print(A @ x)
```

验证：

\[
Ax=b
\]

---

## Day 1 验收

能够回答：

1. `Ax=b` 从 column space 角度是什么意思？
2. 什么情况下 `Ax=b` 无解？
3. pivot 和 rank 有什么关系？
4. Gaussian elimination 为什么能得到 LU？
5. singular matrix 意味着什么？

---

# 6. Day 2：Vector Space、Basis、Rank

这是整门课最重要的一天之一。

## 必学概念

- Vector Space
- Subspace
- Span
- Linear Independence
- Basis
- Dimension
- Rank

---

## 重点理解 Rank

不要只记：

\[
rank(A)=r
\]

应该理解：

> Rank 表示矩阵真正拥有多少个独立方向。

例如：

```python
A = np.array([
    [1., 2.],
    [2., 4.]
])
```

第二列是第一列的倍数。

因此：

\[
rank(A)=1
\]

虽然矩阵有两列，但实际上只有一个独立方向。

---

## NumPy 实验

```python
A = np.array([
    [1., 2.],
    [2., 4.]
])

print(np.linalg.matrix_rank(A))
```

然后稍微扰动：

```python
A = np.array([
    [1., 2.],
    [2., 4.000001]
])

print(np.linalg.matrix_rank(A))
```

开始感受：

```text
数学意义上的 rank
        vs
数值计算意义上的 rank
```

---

## Day 2 验收

回答：

1. Span 是什么？
2. Independent 和 Basis 有什么关系？
3. Dimension 是什么？
4. Rank 为什么不是“矩阵有多少行/列”？
5. Low Rank Matrix 是什么意思？

---

# 7. Day 3：Four Fundamental Subspaces

这一部分是 MIT 18.06 的灵魂之一。

对于：

\[
A\in\mathbb{R}^{m\times n}
\]

需要建立四个空间：

```text
Column Space   C(A)
Null Space     N(A)

Row Space      C(Aᵀ)
Left Null      N(Aᵀ)
```

---

## 必须建立的关系

如果：

\[
rank(A)=r
\]

则：

\[
dim(C(A))=r
\]

\[
dim(C(A^T))=r
\]

\[
dim(N(A))=n-r
\]

\[
dim(N(A^T))=m-r
\]

---

## 两个核心分解

输入空间：

\[
\mathbb{R}^n
=
C(A^T)
\oplus
N(A)
\]

输出空间：

\[
\mathbb{R}^m
=
C(A)
\oplus
N(A^T)
\]

这两个关系非常重要。

---

## Day 3 验收

看到：

\[
A\in\mathbb{R}^{m\times n}
\]

能够立刻想到：

```text
input space  = R^n
output space = R^m

rank = r

Row Space 维度 = r
Null Space 维度 = n-r

Column Space 维度 = r
Left Null Space 维度 = m-r
```

---

# 8. Day 4：Orthogonality、Projection、Least Squares、QR

这是线性代数开始进入“数值计算”的关键点。

---

## Orthogonality

理解：

\[
x^Ty=0
\]

代表两个向量正交。

---

# Projection

如果：

\[
A
\]

的列张成一个 subspace，则把：

\[
b
\]

投影到：

\[
C(A)
\]

得到：

\[
p
\]

满足：

\[
b-p\perp C(A)
\]

所以：

\[
A^T(b-Ax)=0
\]

进一步得到：

\[
A^TAx=A^Tb
\]

这就是 Normal Equation。

---

## Least Squares

当：

\[
Ax=b
\]

没有精确解时：

\[
Ax\approx b
\]

寻找：

\[
\min_x \|Ax-b\|_2
\]

本质上就是 projection。

---

## NumPy

```python
A = np.array([
    [1., 1.],
    [1., 2.],
    [1., 3.]
])

b = np.array([1., 2., 2.])

x, residuals, rank, s = np.linalg.lstsq(
    A,
    b,
    rcond=None
)

print(x)
print(rank)
print(s)
```

---

# QR

理解：

\[
A=QR
\]

其中：

\[
Q^TQ=I
\]

重点是：

> orthogonal matrix 在数值计算中往往非常友好。

---

## Day 4 验收

回答：

1. Projection 是什么？
2. 为什么 Least Squares 等价于 Projection？
3. 为什么得到 \(A^TAx=A^Tb\)？
4. QR 中 Q 为什么重要？
5. 为什么 orthogonal matrix 特别适合数值计算？

---

# 9. Day 5：Eigenvalues、Eigenvectors、Diagonalization

核心公式：

\[
Av=\lambda v
\]

意思是：

> 矩阵作用在某些特殊方向上，只改变长度，不改变方向。

---

## 必学

- Eigenvalue
- Eigenvector
- Characteristic Equation
- Diagonalization

---

## Diagonalization

如果：

\[
A=S\Lambda S^{-1}
\]

那么：

\[
A^k=S\Lambda^kS^{-1}
\]

复杂矩阵运算被转化成：

> 对 eigenvalue 做简单运算。

---

## NumPy

```python
A = np.array([
    [2., 1.],
    [1., 2.]
])

values, vectors = np.linalg.eig(A)

print(values)
print(vectors)
```

验证：

```python
v = vectors[:, 0]
lam = values[0]

print(A @ v)
print(lam * v)
```

---

## Day 5 验收

回答：

1. Eigenvector 为什么特殊？
2. Eigenvalue 表示什么？
3. 为什么 diagonal matrix 特别容易计算？
4. \(A=S\Lambda S^{-1}\) 在做什么？
5. 为什么 \(A^k\) 可以借助 diagonalization 简化？

---

# 10. Day 6：Symmetric Matrix、Positive Definite Matrix

## Symmetric Matrix

\[
A=A^T
\]

这是非常特殊的一类矩阵。

重要性质：

- eigenvalue 为实数；
- eigenvectors 可以构成 orthonormal basis；
- 可以写成：

\[
A=Q\Lambda Q^T
\]

---

# Positive Definite

理解：

\[
x^TAx>0
\]

对于所有：

\[
x\neq0
\]

成立。

不要只把它当定义。

未来会频繁遇到：

```text
Covariance Matrix
Hessian
Optimization
Quadratic Form
Fisher Matrix
```

---

## NumPy

对称矩阵优先：

```python
np.linalg.eigh(A)
```

而不是：

```python
np.linalg.eig(A)
```

---

## Day 6 验收

回答：

1. symmetric matrix 有什么特殊性质？
2. 为什么 eigenvalue 都是实数？
3. PSD / PD 是什么？
4. \(x^TAx\) 有什么几何意义？
5. 为什么 optimization 中大量出现 PSD？

---

# 11. Day 7：SVD

这是第一遍学习的终点，也是最值得投入的 Topic。

对于：

\[
A\in\mathbb{R}^{m\times n}
\]

SVD：

\[
A=U\Sigma V^T
\]

---

## 建立几何理解

可以理解成：

```text
Vᵀ
↓
旋转 / Change of Basis

Σ
↓
沿不同方向缩放

U
↓
再次旋转
```

---

# Singular Values

\[
\sigma_1\geq\sigma_2\geq\dots
\]

表示矩阵在不同方向上的作用强弱。

---

## SVD 与 Rank

\[
rank(A)
=
\#\{\sigma_i>0\}
\]

数值计算中则通常变成：

> 有多少 singular value 显著大于某个 tolerance。

---

# Low-Rank Approximation

如果：

\[
A=U\Sigma V^T
\]

只保留最大的前 \(r\) 个 singular values：

\[
A_r
=
U_r\Sigma_rV_r^T
\]

得到最佳 rank-\(r\) approximation。

这是之后理解：

```text
PCA
Compression
Low-Rank Approximation
LoRA
Model Compression
```

的重要基础。

---

## NumPy

```python
A = np.random.randn(100, 80)

U, S, Vt = np.linalg.svd(
    A,
    full_matrices=False
)

r = 10

A_r = (
    U[:, :r]
    @ np.diag(S[:r])
    @ Vt[:r, :]
)

print(np.linalg.matrix_rank(A_r))
```

---

## Day 7 验收

回答：

1. SVD 三个矩阵分别表示什么？
2. singular value 表示什么？
3. SVD 和 rank 有什么关系？
4. 为什么能做 low-rank approximation？
5. Eigen decomposition 与 SVD 有什么区别？

---

# 12. 必须补充：Condition Number 与 Numerical Stability

虽然它不一定作为 MIT 18.06 最显眼的一条主线，但如果目标包含 AI / 数值计算，必须重点理解。

---

## Near-Singular Matrix

例如：

```python
A = np.array([
    [1.0, 1.0],
    [1.0, 1.000001]
])
```

两行几乎线性相关。

矩阵虽然数学上可能仍可逆，但已经接近 singular。

---

## Condition Number

```python
np.linalg.cond(A)
```

直观理解：

> 输入中的误差，最多可能被矩阵运算放大多少倍。

如果：

\[
\kappa(A)
\]

很大，则矩阵是：

```text
ill-conditioned
```

---

## 实验

```python
A = np.array([
    [1.0, 1.0],
    [1.0, 1.000001]
])

b = np.array([
    2.0,
    2.000001
])

print(np.linalg.cond(A))

x1 = np.linalg.solve(A, b)

b2 = b + np.array([
    0.0,
    1e-6
])

x2 = np.linalg.solve(A, b2)

print(x1)
print(x2)
```

观察：

```text
b 只发生极小变化
        ↓
x 可能发生明显变化
```

这就是：

```text
数学公式相同
≠
数值行为相同
```

---

# 13. 每个 Topic 的统一学习模板

以后所有线性代数 Topic 都可以套：

```text
1. Definition
      ↓
2. Geometric Meaning
      ↓
3. Important Formula
      ↓
4. Tiny Example
      ↓
5. NumPy Verification
      ↓
6. Numerical Issue
      ↓
7. AI / Engineering Connection
```

例如 Rank：

```text
Definition:
独立行/列的数量

Geometric:
矩阵真正保留多少独立方向

Formula:
rank(A)

Example:
[[1,2],
 [2,4]]

NumPy:
np.linalg.matrix_rank(A)

Numerical:
near rank-deficient

AI:
LoRA / low-rank weights
```

---

# 14. 第一遍可以降低优先级的内容

下面这些不是不重要，只是不要阻塞第一遍：

- Determinant 的复杂手算
- Cofactor Expansion
- Cramer's Rule
- Jordan Form
- Markov Matrix
- Graph Applications
- FFT / Fourier Applications
- 大量复杂 inverse 手算

等实际遇到问题再回来补。

---

# 15. 第一遍最终验收

完成后，看到：

\[
A\in\mathbb{R}^{m\times n}
\]

应该能够自然想到：

```text
A 是 linear map

R^n → R^m

输入空间：
Row Space ⊕ Null Space

输出空间：
Column Space ⊕ Left Null Space

rank(A) = r

A 可以进行：

LU
QR
Eigen decomposition（特定条件）
SVD

数值层面还需要考虑：

conditioning
rounding error
precision
near-singular
```

看到：

```python
y = A @ x
```

不只是想到“矩阵乘法”，而是想到：

```text
linear transformation
subspace
rank
basis
singular values
conditioning
```

---

# 16. NumPy → PyTorch 的迁移路线

第一遍 MIT 18.06 完成以后，再开始 PyTorch。

不要重新学一遍数学，只做 API 映射：

| 数学操作 | NumPy | PyTorch |
|---|---|---|
| Matrix Multiply | `A @ B` | `A @ B` |
| Solve | `np.linalg.solve` | `torch.linalg.solve` |
| Rank | `np.linalg.matrix_rank` | `torch.linalg.matrix_rank` |
| QR | `np.linalg.qr` | `torch.linalg.qr` |
| Eigen | `np.linalg.eig` | `torch.linalg.eig` |
| Symmetric Eigen | `np.linalg.eigh` | `torch.linalg.eigh` |
| SVD | `np.linalg.svd` | `torch.linalg.svd` |
| Condition Number | `np.linalg.cond` | `torch.linalg.cond` |

然后再增加 PyTorch 特有概念：

```text
Tensor
dtype
device
autograd
GPU
```

---

# 17. AI / AI-Infra 第二遍路线

完成 Linear Algebra Backbone 后，再从工程问题反向回来：

## Rank

```text
Rank
↓
Low Rank
↓
SVD
↓
Low-Rank Approximation
↓
LoRA
```

## Orthogonality

```text
Orthogonality
↓
Projection
↓
QR
↓
Numerical Stability
```

## Eigenvalue

```text
Eigenvalue
↓
Symmetric / PSD
↓
Covariance
↓
Hessian
↓
Optimization
```

## Ax=b

```text
Ax=b
↓
Near-Singular
↓
Condition Number
↓
Floating Point Error
↓
Training / Numerical Stability
```

## SVD

```text
SVD
↓
Singular Values
↓
Spectrum
↓
Compression
↓
Low-Rank Approximation
↓
Model Analysis
```

---

# 18. 最终建议

整个第一遍学习控制在：

```text
7 天 × 60~90 分钟
```

甚至可以进一步压缩成：

```text
Day 1:
Ax=b + LU + Rank

Day 2:
Four Subspaces

Day 3:
Orthogonality + Projection + Least Squares

Day 4:
QR

Day 5:
Eigen + Symmetric + PSD

Day 6:
SVD

Day 7:
Condition Number + 综合复习
```

学习目标不是：

> “我学完了 MIT 18.06。”

而是：

> **我已经建立一套可以继续学习数值计算、机器学习和 AI Infra 的线性代数骨架。**

这就够了。
